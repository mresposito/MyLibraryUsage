from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import ForeignKey, Column, Integer, String, Boolean
# relations
from sqlalchemy.orm import relationship, backref
import time

Base = declarative_base()

# artist_album_table = 
class Song( Base ):
  __tablename__ = 'song'
  id   = Column( Integer, primary_key = True )

  name          = Column( String)
  artist        = Column( String)
  album_artist  = Column( String)
  composer      = Column( String)
  album         = Column( String)
  genre         = Column( String)
  kind          = Column( String)
  date_modified = Column( String)
  date_added    = Column( String)

  size          = Column( Integer)
  total_time    = Column( Integer)
  track_number  = Column( Integer)
  year          = Column( Integer)
  bit_rate      = Column( Integer)
  sample_rate   = Column( Integer)
  rating        = Column( Integer)
  album_rating  = Column( Integer)
  play_count    = Column( Integer)

  # many to one
  album_id  = Column(Integer, ForeignKey( 'album.id'))
  artist_id = Column(Integer, ForeignKey('artist.id'))
  genre_id  = Column(Integer, ForeignKey( 'genre.id'))

  def __init__( self, attributes ):
    self.name         = attributes.get('Name')
    self.artist       = attributes.get('Artist')
    self.album_artist = attributes.get('Album Artist')
    self.composer     = attributes.get('Composer')
    self.album        = attributes.get('Album')
    self.genre        = attributes.get('Genre')
    self.kind         = attributes.get('Kind')
    self.total_time   = attributes.get('Total Time')
    self.track_number = attributes.get('Track Number')

    if attributes.get('Size'):
      self.size = int(attributes.get('Size'))
    if attributes.get('Year'):
      self.year = int(attributes.get('Year'))
    if attributes.get('Bit Rate'):
      self.bit_rate = int(attributes.get('Bit Rate'))
    if attributes.get('Sample Rate'):
      self.sample_rate = int(attributes.get('Sample Rate'))
    if attributes.get('Play Count'):
      self.play_count = int(attributes.get('Play Count'))
    else:
      self.play_count = 0
    # if attributes.get('Date Modified'):
    #   self.date_modified = time.strptime(attributes.get('Date Modified'), format)
    # if attributes.get('Date Added'):
    #   self.date_added = time.strptime(attributes.get('Date Added'), format)

      # s.comments = attributes.get("Comments ")
      # if attributes.get('Rating'):
      #   s.rating = int(attributes.get('Rating'))
      # s.compilation = 'Compilation' in attributes

  def __repr__( self ):
    return "/song_%d/" % self.id

class Album( Base ): 
  __tablename__ = 'album'
  id   = Column( Integer, primary_key = True )

  name = Column( String)
  play_count = Column(Integer)
  artwork = Column( String )

  # one to many
  songs = relationship('Song', backref=backref("Album") )
  # many to one
  artist_id = Column(Integer, ForeignKey('artist.id'))
  genre_id  = Column(Integer, ForeignKey( 'genre.id'))

  def __init__(self, name):
    self. name = name
    self. play_count = 0

  def __repr__(self):
    return "/album_%d/" % self.id

class Artist( Base ): 
  __tablename__ = 'artist'
  id   = Column( Integer, primary_key = True )

  name = Column( String)
  play_count = Column( Integer )

  # one to many
  songs   = relationship('Song'  , backref=backref("Artist") )
  albums  = relationship('Album' , backref=backref("Artist") )
  # many to one
  genre_id  = Column(Integer, ForeignKey( 'genre.id'))

  def __init__(self, name):
    self. name = name
    self. play_count = 0

  def __repr__(self):
    return "/artist_%d/" % self.id

class Genre( Base ):
  __tablename__ = 'genre'
  id   = Column( Integer, primary_key = True )

  name = Column( String)
  play_count = Column( Integer )
  # one to many
  songs   = relationship('Song'  , backref=backref("Genre") )
  albums  = relationship('Album' , backref=backref("Genre") )
  artists = relationship('Artist', backref=backref("Genre") )

  def __init__(self, name):
    self. name = name
    self. play_count = 0

  def __repr__(self):
    return "/genre_%d/" % self.id
