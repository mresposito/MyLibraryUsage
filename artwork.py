#!/usr/bin/env python
# coding: utf-8
""" main file """

###      @file:  musicImport.py
###
###    @author:  Michele Esposito
###    Company:  myself!

import sys, os, re, string
# http and url
import simplejson
import urllib2, socket, unicodedata, httplib
from urlparse import urlparse
from bs4 import BeautifulSoup, SoupStrainer
# song model
from Song import Song

def getArtwork( album ):
  album_query = process_query( album[0] +" cover") #TODO verify also works for albumart
  
  try:
    artwork_url = queryGoogle( album_query )
    if artwork_url == None:
      artwork_url = queryAlbumart( album_query )
  except urllib2.URLError:
    sys.stderr.write("Could not connect to the internet\n")
    return None

  return artwork_url

def queryAlbumart(album):
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

def queryGoogle( album ):
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
  """ check a given URL is valid """
  try:
    response = urllib2.urlopen( urllib2.Request(path) )
    return True
  except:
    return False

def fetchResults( responseData ):
  """ gets the correct results """
  results = responseData['results']
  for result in results:
    if result.has_key('url') and exists(result['url']):
      return result['url']
