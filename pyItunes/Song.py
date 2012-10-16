import time
class Song:
  """
  Song Attributes:
  name (String)
  artist (String)
  album_arist (String)
  composer = None (String)
  album = None (String)
  genre = None (String)
  kind = None (String)
  size = None (Integer)
  total_time = None (Integer)
  track_number = None (Integer)
  year = None (Integer)
  date_modified = None (Time)
  date_added = None (Time)
  bit_rate = None (Integer)
  sample_rate = None (Integer)
  comments = None (String)
  rating = None (Integer)
  album_rating = None (Integer)
  play_count = None (Integer)
  location = None (String)
  compilation = None (Boolean)
  """
  name        = None
  artist      = None
  album_arist = None
  composer    = None
  album       = None
  genre       = None
  kind        = None
  size        = None
  total_time  = None
  track_number= None
  year        = None
  date_modified = None
  date_added  = None
  bit_rate    = None
  sample_rate = None
  rating      = None
  album_rating = None
  play_count  = None
  compilation = None

  def __init__( self, attributes ):
    format = "%Y-%m-%dT%H:%M:%SZ"
    self.name = attributes.get('Name')
    self.artist = attributes.get('Artist')
    self.album_artist = attributes.get('Album Aritst')
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
    if attributes.get('Date Modified'):
      self.date_modified = time.strptime(attributes.get('Date Modified'),format)
    if attributes.get('Date Added'):
      self.date_added = time.strptime(attributes.get('Date Added'),format)
    if attributes.get('Bit Rate'):
      self.bit_rate = int(attributes.get('Bit Rate'))
    if attributes.get('Sample Rate'):
      self.sample_rate = int(attributes.get('Sample Rate'))
    if attributes.get('Play Count'):
      self.play_count = int(attributes.get('Play Count'))
      # s.comments = attributes.get("Comments ")
      # if attributes.get('Rating'):
      #   s.rating = int(attributes.get('Rating'))

      # s.compilation = 'Compilation' in attributes
