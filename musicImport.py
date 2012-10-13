#!/usr/bin/env python
# coding: utf-8
""" main file """

###      @file:  manage.py
###
###    @author:  Michele Esposito
###    Company:  Bot Square Inc.

import sys, os, re, optparse
from xml.dom import minidom
from pyItunes import *
from mutagen import *
import urllib2
from urlparse import urlparse

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

def checkFile(file):
  """ check whether a file exists or not """
  if not os.path.exists(file):
    sys.stderr.write( "invalid file:%s " % file )
    raise IOError

class Cmdline:
  """ dummy class to keep all variables """
  pass

class OrderedLibrary:
  """ class to show usage """
  library = None
  top_artist = None
  top_album = None
  top_genre = None
  numberSongs = 0

  toShow = 10

  def __init__(self, library):
    print "parsing library"
    pl = XMLLibraryParser( library )
    self.library = Library( pl.dictionary )
    self.numberSongs = len( self.library.songs )
    self.topStats()

  def topStats(self):
    """ find the top of everything """
    print "******  Artist "
    artist = lambda x : x.artist
    self.top_artist = findTop( artist, self.library, self.toShow )
    print "******  Albums "
    album = lambda x : x.album
    self.top_album  = findTop( album, self.library, self.toShow  )
    print "******  Genre  "
    genre = lambda x : x.genre
    self.top_genre = findTop( genre,  self.library, self.toShow  )

  def usageStats(self):
    """ prints more statistics on usage """
    print "*** Usage stats ***"
    self.numberListened = 0
    self.totalPlayCount = 0
    self.totalTime = 0
    for song in self.library.songs:
      if song.play_count > 0:  
        self.numberListened += 1
        self.totalPlayCount += song.play_count
        self.totalTime += song.play_count * int(song.total_time)

    print "Number of songs: %d" % self.numberSongs 
    print "Songs listened to: %d (%2.1f%%)"  % ( self.numberListened, x100(self. numberListened, self.numberSongs) )
    print "Total play count: %d " % self. totalPlayCount
    print "You have listened to:", convertToDMH( self.totalTime, 3 ), "of music"


  def getArtwork(self):
    """ retrive the artwork of an album """
    for album in self.top_album:
      for song in album:
        try: 
          album_path = HTTPToPath( song.location )
          track_path = File( album_path ) 

          artwork = track_path.tags['APIC:'].data
          artwork_name = os.path.join( 'tmp/artwork',  album[0]+'.jpg') 
          with open( artwork_name, 'w') as img:
            verbosePrint( "track path: %s" % album_path, 1 )
            verbosePrint( artwork_name, 1 )
            img.write( artwork  )
            break
        except KeyError:
          pass
  
def findTop ( attribute, library, topNum ): # TODO: refactor
  tops = []
  for song in library.songs:
    if not attribute(song) in tops:
      tops.append( attribute(song) )

  tops_count = []    
  for top in tops:
    count = 0
    songs = []
    for song in library.songs:
      if attribute(song) == top:
        songs. append( song )
        try: count += song.play_count
        except TypeError: pass
    # sort by increasing play count
    songs = sorted ( songs, key = lambda x:x.play_count, reverse=True )
    tops_count. append( (top, count, songs) )

  tops_count = sorted( tops_count, key = lambda x:x[1], reverse=True )
  
  totalCount = 0
  for i in range(0, topNum):
    totalCount += tops_count[i][1]

  top_short = []

  for i in range(0, topNum):
    top_short.append( tops_count[i] )
    printOut( "%d) %s          Play count: %d (%2.1f%%)" % (i+1, tops_count[i][0], tops_count[i][1], x100( tops_count[i][1], totalCount )))
  return top_short

def x100( per, cent ):
  """ returns percentage """
  return per * 100 / cent


#     for filterWrap in Cmdline.filters:
#       filter = filterWrap['Filter']
#       total_count = len( filter( Cmdline ) )
#       listened_count = len( [ needle for needle in filter( Cmdline ) if play_count( needle ) > 0])
#       print "Number of %s: %d" %( filterWrap['Print'], total_count )
#       print filterWrap['Print']," listened: %d (%2.1f%%)" % ( listened_count, x100(listened_count, total_count) )
#         


def verbosePrint( message, level ):
  """ wrapper for verbose print """
  if Cmdline.options.verbose > level:
    printOut( message )

def backupLibrary():
  """ for safety, backup the library before using it. """
  # TODO: implement!!
  pass

def parseCmdline( ):
  usage = \
  """
  Usage: %prog <mode> <log_files>
  Examples:
      python ./manage.py stats
      python ./manage.py ~/Music/library.xml
  """

  parser = optparse.OptionParser( usage)
  group  = optparse.OptionGroup ( parser, "Options")

  group.add_option("-v", "--verbose", type="int", default=0, help="Verbosity", dest="verbose")
  group.add_option("-t", "--toShow",  type="int", default=20, help="Results to show", dest="toShow")
  group.add_option("-u", "--unique",  type="int", default=20, help="Results to show", dest="toShow")
  parser.add_option_group( group)
  Cmdline.options, Cmdline.args = parser.parse_args()

  Cmdline.stats = Cmdline.args[0] == "stats"
  Cmdline.library = Cmdline.args[0]
  checkFile( Cmdline.library )

  Cmdline.backup = Cmdline.library # FIXME! backup the library

def printOut( message ):
  print decode_unicode_references( message )

def convertToDMH( time, measure ):
  """ returns number of days, hours, minutes """
  unit = 0
  string = ""
  if  measure == 0:
    return string
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

def HTTPToPath( HTTPPath ):
  """ convert from HTTP To Path"""
  HTTPPath =  decode_unicode_references( HTTPPath ).encode('UTF-8')
  o = urlparse( urllib2.url2pathname( HTTPPath ) )
  return o.path

def main():
  """ main function """
  parseCmdline()

  print "reading library"
  backupLibrary()

  stats = OrderedLibrary( Cmdline.backup )
  print "evaluating statistics"
  stats. usageStats()
  stats. getArtwork()

if __name__=="__main__":
  """ call module """
  main()
