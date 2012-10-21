from sqlalchemy import ForeignKey, Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
import time

Base = declarative_base()

class Song( Base ):
  __tablename__ = 'songs'
  id   = Column( Integer, primary_key = True )

  name        = Column( String) 
  artist      = Column( String) 
  album_arist = Column( String) 
  composer    = Column( String) 
  album       = Column( String) 
  genre       = Column( String) 
  kind        = Column( String) 
  date_modified = Column( String)
  date_added  = Column( String  )

  size        = Column( Integer) 
  total_time  = Column( Integer) 
  track_number = Column( Integer) 
  year        = Column( Integer) 
  bit_rate    = Column( Integer )
  sample_rate = Column( Integer )
  rating      = Column( Integer )
  album_rating = Column( Integer)
  play_count  = Column( Integer )

  def __init__( self, attributes ):
    format = "%Y-%m-%dT%H:%M:%SZ"
    self.name = attributes.get('Name')
    self.artist = attributes.get('Artist')
    self.album_artist = attributes.get('Album Artist')
    self.composer = attributes.get('Composer')
    self.album = attributes.get('Album')
    self.genre = attributes.get('Genre')
    self.kind = attributes.get('Kind')
    self.total_time = attributes.get('Total Time')
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
    # if attributes.get('Date Modified'):
    #   self.date_modified = time.strptime(attributes.get('Date Modified'), format)
    # if attributes.get('Date Added'):
    #   self.date_added = time.strptime(attributes.get('Date Added'), format)

      # s.comments = attributes.get("Comments ")
      # if attributes.get('Rating'):
      #   s.rating = int(attributes.get('Rating'))
      # s.compilation = 'Compilation' in attributes

  def __repr__( self ):
    print "Name:", self.name," by:", self.artist
