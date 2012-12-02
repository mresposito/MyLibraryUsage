from django.http import HttpResponse, HttpResponseRedirect
from datetime import datetime
import time, json, sys

### DECORATORS ###
def get_required( fun ):
  def wrapper(*args, **kwargs):
    if args[0].method != "GET":
      return HttpResponseRedirect('/home/')

    return fun( *args, **kwargs )
  return wrapper

def post_required( fun ):
  def wrapper(*args, **kwargs):
    if args[0].method != "POST":
      return HttpResponseRedirect('/home/')

    return fun( *args, **kwargs )
  return wrapper

### UTIL FUNCTIONS ###
def getDataToJson( data ):
  return json.dumps( data )

def contentToHTML( content ):
  return content.replace('\r\n','<br>')

def HTMLToContent( content ):
  return content.replace('<br>','\n')

def dateToTimestamp( date ):
  tmp = date.split("/")
  if len( tmp ) < 1 or len( tmp ) > 3:
    sys.stderr.write("invalid date\n")
    sys.exit()
  if len( tmp ) == 1:
    date = datetime(2012, 10, int(tmp[0]))
  elif len( tmp ) == 2:
    date = datetime(2012, int(tmp[0]), int(tmp[1]))
  else:
    date = datetime( int(tmp[0]), int(tmp[1]), int(tmp[2]))

  return time.mktime( date.timetuple() )
 
def timestampToDate( timestamp ):
  return datetime.fromtimestamp( timestamp ).strftime('%Y/%m/%d')

def todaysDate():
  now = time.mktime( datetime.today().timetuple() )
  return timestampToDate( now )
