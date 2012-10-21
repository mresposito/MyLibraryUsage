#!/usr/bin/env python
# coding: utf-8
""" main file """

###      @file:  musicImport.py
###
###    @author:  Michele Esposito
###    Company:  myself!

import sys, os, re, string
import simplejson
# parse itunes library
from xml.dom import minidom
from pyItunes import XMLLibraryParser
from Song import Song, Base
# http and url
import urllib2, socket, unicodedata, httplib
from urlparse import urlparse
from bs4 import BeautifulSoup, SoupStrainer
# database stuff
from sqlalchemy     import create_engine, func
from sqlalchemy.orm import sessionmaker
# graphs
from chartit import DataPool, Chart
# artwork
from artwork import getArtwork

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
  numberSongs = 0
  toShow = 10
  database = None
  session  = None

  def __init__(self, database):
    self.database= database
    self.setupConnection()

  def addItunesLibrary( self, library ):
    print "parsing library"
    pl = XMLLibraryParser( library )
    print "writing library to database"
    for song,attributes in pl.dictionary.iteritems():
      self.session.add( Song( attributes ) )
    # update changes to db
    self.commitSession()
    
  def commitSession( self ):
    self.session.commit()

  def setupConnection( self ):
    """ connect to desired DB """
    if self.database == None:
      sys.stderr.write( "database name not specified\n")
      return

    engine  = create_engine ( 'sqlite:///'+self.database )

    if not os.path.exists( self.database ):
      Base.metadata.create_all( engine )

    Session = sessionmaker ( )
    Session.configure( bind=engine )
    self.session = Session ()

  def usageStats(self):
    songs = self.session.query(Song)
    self.numberSongs = songs.count()
    # general
    listenedSongs    = self.session.query(Song).filter( Song.play_count>0 )
    self.listenedSongs = listenedSongs.count()
    self.notListenedSongs = self.numberSongs - self.listenedSongs
    self.totalPlayCount = sumPlayCountQuery( listenedSongs )
    self.DMH = calculateDMH( listenedSongs )
    # bit rates
    bit_rates = [ 320, 256, 224, 192, 160, 128, 122, 96, 80 ]

    self.quality = []
    for rate in bit_rates:
      query = self.session.query(Song).filter( Song.bit_rate == rate ).count()
      triple = ( rate, query, x100( query, self.numberSongs ) )
      if triple[2] > 3:
        self.quality.append( triple )

    self.lenght = []
    for i in range(0,8):
      toMinutes = lambda x:x*60*1000
      query = self.session.query(Song).filter( Song.total_time >= toMinutes(i), Song.total_time < toMinutes(i+1) ).count()
      triple = ( i, query, x100( query, self.numberSongs ) )
      self.lenght.append( triple )

  def artistStats(self):
    self.numberSongs = self.session.query(Song).count()
    artist = lambda x : x.artist
    self.top_artist = self.findTop( artist)
    print "finished"

  def albumStats(self):
    self.numberSongs = self.session.query(Song).count()
    album = lambda x : x.album
    self.top_album = self.findTop( album)
    print "finished"

  def findArtwork(self):
    # if self.has_attr('top_album'):
    #   sys.stderr.write( "you must run albumStats before\n")
    for album in self.top_album:
      album[3] = getArtwork( album ) 

  def genreStats(self):
    self.numberSongs = self.session.query(Song).count()
    genre = lambda x : x.genre
    self.top_genre = self.findTop( genre)
    print "finished"

  def findTop (self, attribute ): # TODO: refactor
    tops = self.session.query(attribute(Song)).distinct()

    tops_count = []    
    for top in tops:
      songs = self.session.query(Song).filter( attribute(Song)== attribute(top) )
      count = sumPlayCountQuery( songs )
      # sort by increasing play count
      songs = sorted ( songs, key = lambda x:x.play_count, reverse=True )
      tops_count. append( [ attribute(top), count, songs, None ] )

    tops_count = sorted( tops_count, key = lambda x:x[1], reverse=True )
    
    totalCount = 0
    for i in range(0, self.toShow ):
      totalCount += tops_count[i][1]

    top_short = []

    for i in range(0, self.toShow ):
      top_short.append( tops_count[i] )
      print "%d) %s          Play count: %d (%2.1f%%)" % (i+1, tops_count[i][0], tops_count[i][1], x100( tops_count[i][1], totalCount ))
    return top_short
  
def sumPlayCountQuery( query ):
  total = 0
  for song in query:
    if song.play_count != None:
      total += song.play_count
  return total

def x100( per, cent ):
  """ returns percentage """
  return per * 100 / cent

def calculateDMH( query ):
  time = 0
  for song in query:
    time += song.play_count * int(song.total_time)
  return convertToDMHWrapped( time, 3 )

def convertToDMHWrapped( time, measure ):
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
    return convertToDMHWrapped( time, measure - 1 )

  num = int( time / unit )
  string = "%d " % num + message +" " 

  return string + convertToDMHWrapped( time - num*unit, measure - 1 )
