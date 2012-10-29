#!/usr/bin/env python
# coding: utf-8
""" main file """

###      @file:  musicImport.py
###
###    @author:  Michele Esposito
###    Company:  myself!

import sys, os, re, time
# parse itunes library
from pyItunes import XMLLibraryParser
from Library import Base, Song, Artist, Album, Genre
# database stuff
from sqlalchemy     import create_engine
from sqlalchemy.orm import sessionmaker
# artwork
# from artwork import getArtwork

 
class Librarian:
  """ class to manipulate library"""
  numberSongs = 0
  toShow = 10
  database = None
  session  = None

  def __init__(self, database):
    """ connect to DB """
    self.database= database
    self.setupConnection()

  def addSongsfromXML( self, library ):
    """ parses itunes library, adds songs into DB """
    self.startTimer( "parsing library")
    pl = XMLLibraryParser( library )
    self.stopTimer()
    self.startTimer( "writing library to database")
    for song,attributes in pl.dictionary.iteritems():
      song = Song(attributes) 
      self.session.add( Song( attributes ) )
    # update changes to db
    self.stopTimer()
    print "committing session"
    self.commitSession()

  def getRequest(self, request):
    request = request.replace('/','').split("_")
    cls = request[0]
    request_id = int(request[1])
    print "request: %s id: %d " %( cls, request_id)
    toReturn = None
    if cls == "song":
      toReturn = self.session.query(Song).filter(Song.id == request_id).all()
    elif cls == "album":
      toReturn = self.session.query(Album).filter(Album.id == request_id).all()
      self.linkAlbum( toReturn )
    elif cls == "artist":
      toReturn = self.session.query(Artist).filter(Artist.id == request_id).all()
      self.linkArtist( toReturn )
    elif cls == "genre":
      toReturn = self.session.query(Genre).filter(Genre.id == request_id).all()
      self.linkGenre ( toReturn )
    return toReturn

  def link( self, obj, attribute, toLink ):
    needles = self.session.query( attribute(Song) ).filter( attribute(Song) == obj.name )
    haysack = []
    for needle in needles:
      haysack.append( self.session.query( toLink ).filter( toLink.name == needle[0] ) )
    return haysack

  def linkAlbum( self, obj ):
    obj = obj[0]
    obj. artists = self.link( obj, lambda x:x.artist, Artist ) 
    # obj. genres  = self.link( obj, lambda x:x.genre , Genre  ) 

  def linkArtist( self, obj ):
    obj = obj[0]
    obj. albums  = self.link( obj, lambda x:x.album , Album  ) 
    # obj. genres  = self.link( obj, lambda x:x.genre , Genre  ) 

  def linkGenre( self, obj ):
    obj = obj[0]
    obj. albums  = self.link( obj, lambda x:x.album , Album  ) 
    obj. artists = self.link( obj, lambda x:x.artist, Artist ) 

  def create(self, attribute, toCreate):
    songs= self.session.query( Song ).order_by( attribute(Song))
    album_to_add = toCreate ( attribute( songs[0] ) )
    total = 0

    for song in songs:
      if album_to_add.name != attribute( song ):
        album_to_add.play_count = total
        self.session.add( album_to_add  )
        album_to_add = toCreate( attribute(song))
        total = 0

      album_to_add.songs.append( song )
      total += song.play_count
  
    self.session.commit()  

  def calculatePlayCount( self ):
    self.startTimer("start count")
    print "hey"
    self.stopTimer()
  
  def createNew(self, attribute, toCreate):
    albums_list = self.session.query( attribute(Song) ).distinct()
    for album in albums_list:
      self. session.add( toCreate( album[0] ) )
   
  def createEntries ( self ):
    self.startTimer( "counting" )
    self.create ( lambda x:x.genre  , lambda x: Genre   ( x) )
    self.create ( lambda x:x.artist , lambda x: Artist ( x) )
    self.create ( lambda x:x.album  , lambda x: Album(x) )
    # self.link()
    self.session.commit()  
    self.stopTimer()

  def createEntriesOld( self ):
    """ creates Album, Artist, Genre classes.
        links them and calculates playcount """
    print "starting creating"
    self.startTimer( "counting" )
    self.create ( lambda x:x.genre, lambda x: Genre(x) )
    self.stopTimer()
    self.create ( lambda x:x.artist, lambda x: Artist(x) )
    self.stopTimer()
    self.create ( lambda x:x.album, lambda x: Album(x) )
    self.stopTimer()
    print "Finish creating, starting to link"

  def commitSession( self ):
    self.session.commit()

  def setupConnection( self ):
    """ connect to desired DB """
    if self.database == None:
      sys.stderr.write( "database name not specified\n")
      return
    print "connecting to database: %s" % self.database
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

  def generateLists( self, toShow ):
    top_song  = sorted( self.session.query(Song), \
      key=lambda x:x.play_count, reverse=True )
    self.top_song = getFromList( top_song, toShow )

    top_album = sorted( self.session.query(Album), \
        key=lambda x:x.play_count, reverse=True )
    self.top_album = getFromList( top_album, toShow )

    top_artist = sorted( self.session.query(Artist), \
        key=lambda x:x.play_count, reverse=True )
    self.top_artist = getFromList( top_artist, toShow )

    top_genre = sorted( self.session.query(Genre), \
        key=lambda x:x.play_count, reverse=True )

    self.top_genre = getFromList( top_genre, toShow )
  
  ##### MISCELANEOUS
  def startTimer(self, message):
    print message
    self.timer = time.time()

  def stopTimer(self ):
    print "Took: %0.3f ms" % ( time.time() - self.timer )

  def findArtwork(self):
    # if self.has_attr('top_album'):
    #   sys.stderr.write( "you must run albumStats before\n")
    return
 
  ##### END OF LIBRARIAN CLASS #####
def getFromList( lst, toShow ):
  count = 0
  ret   = []
  for l in lst:
    if count >= toShow:
      break
    ret. append(l)
    count += 1
  return ret

def sumPlayCountQuery( query ):
  total = 0
  for song in query:
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
