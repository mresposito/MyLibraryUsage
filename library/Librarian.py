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
from library.artwork import getImage
# colors
import colorsys
from webcolors import rgb_to_hex

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

    toReturn = None
    data     = None

    if cls == "song":
      toReturn = self.session.query(Song).filter(Song.id == request_id).all()[0]

    elif cls == "album":
      toReturn = self.session.query(Album).filter(Album.id == request_id).all()[0]

      artists  = self.session.query(Song).filter( Song.album == toReturn.name ). \
                  distinct(Song.artist)
      genres = self.session.query(Song).filter( Song.album == toReturn.name ). \
                  distinct(Song.genre)
      if toReturn.image == None and toReturn != None:
        toReturn.image = getImage( "%s %s" % (toReturn.name, toReturn.songs[0].Artist.name), "album" )

      data = { 'artists': sanitize(artists, lambda x:x.artist),\
                'genres': sanitize(genres , lambda x:x.genre )}

    elif cls == "artist":
      toReturn = self.session.query(Artist).filter(Artist.id == request_id).all()[0]

      albums  = self.session.query(Song).filter( Song.artist == toReturn.name ). \
                  distinct()
      genres = self.session.query(Song).filter( Song.artist == toReturn.name ). \
                  distinct()

      data = { 'genres': sanitize(genres, lambda x:x.genre) ,\
               'albums': sanitize(albums, lambda x:x.album) }

      if toReturn.image == None and toReturn != None:
        toReturn.image = getImage( toReturn.name, "artist" )

    elif cls == "genre":
      toReturn  = self.session.query(Genre).filter(Genre.id == request_id).all()[0]

      artists  = self.session.query(Song).filter( Song.genre == toReturn.name ). \
                  distinct()
      albums   = self.session.query(Song).filter( Song.genre == toReturn.name ). \
                  distinct()

      data = { 'artists': sanitize(artists, lambda x:x.artist),\
                'albums': sanitize(albums , lambda x:x.album )}

    self.commitSession()
    return toReturn, data

  def create(self, attribute, toCreate):
    songs= self.session.query( Song ).order_by( attribute(Song))
    album_to_add = toCreate ( attribute( songs[0] ) )

    for song in songs:
      if album_to_add.name != attribute( song ):
        self.session.add( album_to_add  )
        album_to_add = toCreate( attribute(song))

      album_to_add.songs.append( song )
      album_to_add.play_count += song.play_count

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
    self.create ( lambda x:x.genre  , lambda x: Genre ( x))
    self.create ( lambda x:x.artist , lambda x: Artist( x))
    self.create ( lambda x:x.album  , lambda x: Album ( x))
    self.session.commit()
    self.stopTimer()

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

    colors = createColors( (75,0,130), 9,2 )
    self.quality = []
    for (i, rate) in enumerate(bit_rates):
      query = self.session.query(Song).filter( Song.bit_rate == rate ).count()
      if x100( query, self.numberSongs) > 2: # filter lower rate
        self.quality.append( ( query, "%d kbps" %rate, colors[i] ))

    self.lenght = []
    colors = createColors( (50,0,240), 9, 1 )
    print colors
    for i in range(0,8):
      toMinutes = lambda x:x*60*1000
      query = self.session.query(Song).filter( Song.total_time. \
          between( toMinutes(i),toMinutes(i+1) )).count()
      message = "%d" % (i+1)
      self.lenght.append( (query, message, colors[i ]) )

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

def createColors ( baseColor, number, space ):
  if space == 0:
    generarate = lambda x: (baseColor[0]+x , baseColor[1]    , baseColor[2])
  elif space == 1:
    generarate = lambda x: (baseColor[0]   , baseColor[1] +x , baseColor[2])
  else:
    generarate = lambda x: (baseColor[0]+x , baseColor[1]    , baseColor[2]+x)

  step = (255-baseColor[space]) / number
  colors = []
  for i in range(number):
    toAdd =  generarate( step * i )
    colors.append( toAdd )
  return map( rgb_to_hex, colors )

def sanitize( query, action ): #TODO awful logic, this has to be cleaned
  ret = []
  retNames = []
  for element in query:
    if action(element) not in retNames:
      retNames.append( action(element) )
      ret.append( element )
  return sorted( ret, key=lambda x:x.play_count, reverse=True)
