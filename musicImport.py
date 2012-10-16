#!/usr/bin/env python
# coding: utf-8
""" main file """

###      @file:  manage.py
###
###    @author:  Michele Esposito
###    Company:  Bot Square Inc.

import sys, os, re, optparse, string
import simplejson
from xml.dom import minidom
from pyItunes import Song, XMLLibraryParser
import urllib2, socket, unicodedata, httplib
from urlparse import urlparse
from bs4 import BeautifulSoup, SoupStrainer
import time

socket.setdefaulttimeout(3) #Set a 20 second timeout for Urllib 

def _callback(matches):
  """ fun for decoding """
  id = matches.group(1)
  try:
    return unichr(int(id))
  except:
    return id

def decode_unicode_references(data):
  """ decode function for unicode """
  return re.sub("&#(\d+)(;|(?=\s))", _callback, data)

class Library:
  """ class to show usage """
  artists = None
  albums = None
  genres = None
  songs  = []
  numberSongs = 0

  toShow = 10

  def __init__(self, library):
    print "parsing library"
    pl = XMLLibraryParser( library )
    print "generating library"
    self.parseDictionary(pl.dictionary)
    self.numberSongs = len( self.songs )
    self.topStats()

  def parseDictionary(self,dictionary):
    songs = []
    format = "%Y-%m-%dT%H:%M:%SZ"
    for song,attributes in dictionary.iteritems():
      s = Song( attributes )
      self.addToLibrary(s)
  
  def addToLibrary(self, song):
    self.songs.append(song)
    # add artist
    # add album
    # add genre

  def topStats(self):
    """ find the top of everything """
    print "******  Artist "
    artist = lambda x : x.artist
    self.top_artist = self.findTop( artist)
    print "******  Albums "
    album = lambda x : x.album
    self.top_album  = self.findTop( album )
    print "******  Genre  "
    genre = lambda x : x.genre
    self.top_genre  = self.findTop( genre )

    for album in self.top_album:
      art = getGoogleArtwork( album[0]+" "+album[2][0].artist )
      print art
      if art == None:
        art = getArtwork( album[0] )
      album[3] = art

  def findTop (self, attribute ): # TODO: refactor
    tops = []
    for song in self.songs:
      if not attribute(song) in tops:
        tops.append( attribute(song) )

    tops_count = []    
    for top in tops:
      count = 0
      songs = []
      for song in self.songs:
        if attribute(song) == top:
          songs. append( song )
          try: count += song.play_count
          except TypeError: pass
      # sort by increasing play count
      songs = sorted ( songs, key = lambda x:x.play_count, reverse=True )
      tops_count. append( [ top, count, songs, None ] )

    tops_count = sorted( tops_count, key = lambda x:x[1], reverse=True )
    
    totalCount = 0
    for i in range(0, self.toShow ):
      totalCount += tops_count[i][1]

    top_short = []

    for i in range(0, self.toShow ):
      top_short.append( tops_count[i] )
      printOut( "%d) %s          Play count: %d (%2.1f%%)" % (i+1, tops_count[i][0], tops_count[i][1], x100( tops_count[i][1], totalCount )))
    return top_short

  def usageStats(self):
    """ prints more statistics on usage """
    print "*** Usage stats ***"
    self.numberListened = 0
    self.totalPlayCount = 0
    self.totalTime = 0
    for song in self.songs:
      if song.play_count > 0:  
        self.numberListened += 1
        self.totalPlayCount += song.play_count
        self.totalTime += song.play_count * int(song.total_time)

    print "Number of songs: %d" % self.numberSongs 
    print "Songs listened to: %d (%2.1f%%)"  % ( self.numberListened, x100(self. numberListened, self.numberSongs) )
    print "Total play count: %d " % self. totalPlayCount
    print "You have listened to:", convertToDMH( self.totalTime, 3 ), "of music"


def x100( per, cent ):
  """ returns percentage """
  return per * 100 / cent

def printOut( message ):
  print decode_unicode_references( message )

def convertToDMH( time, measure ):
  """ returns number of days, hours, minutes """
  unit = 0
  if  measure == 0:
    return ""
  if measure > 0:
    message = "minutes"
    unit = 1000*60
  if measure > 1:
    message = "hours,"
    unit *=  60
  if measure > 2:
    message = "days,"
    unit *=  24

  if unit > time:
    return convertToDMH( time, measure - 1 )

  num = int( time / unit )
  string = "%d " % num + message +" " 

  return string + convertToDMH( time - num*unit, measure - 1 )

def getArtwork(album):
  album = process_query( album +" cover")
  print "Art engine Retrieve art for", album
  url = 'http://www.albumart.org/index.php?skey=%s&itempage=1&newsearch=1&searchindex=Music' % album
  page = urllib2.urlopen(url)
  page = page.read()
  soup = BeautifulSoup( page )
  for image in soup.find_all('img'):
    if image.has_key('src') and image.has_key('class'):
      return image['src']

def process_query( album ):
  album = unicodedata.normalize('NFKD', u'%s'% album).encode('ascii', 'ignore')
  album = album.split(' ')
  album = string.join(album, '%20')
  album = album.replace(':','')
  album = album.replace(',','')
  album = album.replace('/', '+')
  return album

def getGoogleArtwork( album ):
  album = process_query( album )
  print "Google Retrieve art for", album
  url = ('https://ajax.googleapis.com/ajax/services/search/images?' +
         'v=1.0&q=' + album)

  request = urllib2.Request(url, None, {'Referer':None})
  try:
    response = urllib2.urlopen(request).read()
  except urllib2.HTTPError:
    sys.stderr.write("bad request: %s" % url)
    return None

  results = simplejson.loads( response )
  try: 
    return fetchResults( results['responseData'] )
  except KeyError:
    sys.stderr.write("no valiable response for artwork %s" % album)
  except TypeError:
    print results
    sys.stderr.write("no match for artwork %s" % album)
  return None

def exists(path):
  try:
    response = urllib2.urlopen( urllib2.Request(path) )
    return True
  except:
    return False

def fetchResults( responseData ):
  results = responseData['results']
  for result in results:
    if result.has_key('url') and exists(result['url']):
      return result['url']

def formatSong(s, attributes ):
  s = Song()
  s.name = attributes.get('Name')
  s.artist = attributes.get('Artist')
  s.album_artist = attributes.get('Album Aritst')
  s.composer = attributes.get('Composer')
  s.album = attributes.get('Album')
  s.genre = attributes.get('Genre')
  s.kind = attributes.get('Kind')
  if attributes.get('Size'):
    s.size = int(attributes.get('Size'))
  s.total_time = attributes.get('Total Time')
  s.track_number = attributes.get('Track Number')
  if attributes.get('Year'):
    s.year = int(attributes.get('Year'))
  if attributes.get('Date Modified'):
    s.date_modified = time.strptime(attributes.get('Date Modified'),format)
  if attributes.get('Date Added'):
    s.date_added = time.strptime(attributes.get('Date Added'),format)
  if attributes.get('Bit Rate'):
    s.bit_rate = int(attributes.get('Bit Rate'))
  if attributes.get('Sample Rate'):
    s.sample_rate = int(attributes.get('Sample Rate'))
  if attributes.get('Play Count'):
    s.play_count = int(attributes.get('Play Count'))
# if attributes.get('Location'):
      #   s.location = attributes.get('Location')     
      # s.comments = attributes.get("Comments ")
      # if attributes.get('Rating'):
      #   s.rating = int(attributes.get('Rating'))

      # s.compilation = 'Compilation' in attributes
