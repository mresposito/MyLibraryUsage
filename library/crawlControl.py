#!/usr/bin/env python
# coding: utf-8
""" main file """

###      @file:  crawlControl.py
###
###    @author:  Michele Esposito
###    Company:  myself!

import sys, os, string, re
# parse itunes library
from library.Library import Base, Artist, Album
# database stuff
from sqlalchemy     import create_engine
from sqlalchemy.orm import sessionmaker
# json
import simplejson
from simplejson.decoder import JSONDecodeError
# http and url
import urllib2, unicodedata
from bs4 import BeautifulSoup, SoupStrainer

DATABASE = os.path.abspath("databases/images.db")
print DATABASE
 
class Crawler:
  """ class to manipulate library"""
  numberSongs = 0
  toShow = 10
  database = None
  session  = None

  def __init__( self ):
    """ connect to DB """
    self.setupConnection()

  def commitSession( self ):
    self.session.commit()

  def setupConnection( self ):
    """ connect to desired DB """
    engine  = create_engine ( 'sqlite:///'+ DATABASE )

    if not os.path.exists( DATABASE ):
      Base.metadata.create_all( engine )

    Session = sessionmaker ( )
    Session.configure( bind=engine )
    self.session = Session ()

  def start( self ):
    # page      = readPage( entry_point ) 
    # subgenres = getSubgenres( page )
    page = queryWikipage( 'Metallica' )

    print getArtistInfo( page )
  
def queryWikipage( query ):
  """ returns page in json """
  url = 'http://en.wikipedia.org/w/api.php?action=query&prop=revisions&rvprop=content&format=json&titles=%s' % normalize_query( query )

  return requestJsonUrl ( url, )

def queryWikipageLinks( query ):
  """ returns page in json """
  url = 'http://en.wikipedia.org/w/api.php?action=query&prop=revisions&format=json&titles=%s' % normalize_query( query )

  return requestJsonUrl ( url, )

def getSubgenres( page ):
  complete_list = None
  for link in page.find_all('a'):
    if '(complete list)' in  link:
      complete_list = link
      break

  return complete_list 

### EXTRACT INFO ###

def getArtistInfo( page ):
  """ page is in json """
  title, content = readWikiPage( page ) 
  image  = getImage( content )
  albums = getAlbums( title, content )

def getImage ( content ):
  img = re.search('image.=.*\n', content).group(0)
  url = 'https://upload.wikimedia.org/wikipedia/commons/3/3e/' # or try file
  return url+ img.lstrip('image = ').replace(" ","_")

def getAlbums( title, content ):
  if re.search( '[[Discography]]', content ):
    page = queryWikipageLinks( title + ' discography' )
    print page
    newTitle, content = readWikiPage( page )
    for line in content:
      print line
      
     
### Functions to read pages ###
def loadHTMLURl ( url ):
  page = urllib2.urlopen(url)
  page = page.read()
  return BeautifulSoup( page )

def requestJsonUrl ( url ):
  request = urllib2.Request(url, None, {'Referer':None})
  try:
    response = urllib2.urlopen(request).read()
  except urllib2.HTTPError:
    sys.stderr.write("bad request: %s" % url)
    return None

  try:
    return simplejson.loads( response )
  except JSONDecodeError:
    sys.stderr.write("could not parse: \n %s \n" % response )
    return None

def readWikiPage( page ):
  keys =  page['query']['pages'].keys()
  if len( keys ) > 1:
    print "MULTIPLE QUERIES!"

  page = page['query']['pages'][keys[0]]

  return page['title'], page['revisions'][0]['*']

### UTILS ###
def normalize_query( album ):
  album = unicodedata.normalize('NFKD', u'%s'% album).encode('ascii', 'ignore')
  album = album.split(' ')
  album = string.join(album, '%20')
  album = album.replace(':','')
  album = album.replace(',','')
  album = album.replace('/', '+')
  return album
