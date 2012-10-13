import time, uuid
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseServerError, HttpResponseRedirect
from django.shortcuts import render, render_to_response
from django.template import RequestContext
from musicImport import *

def home(request):

  return render_to_response('home.html',{},context_instance=RequestContext(request))

def statistics(request):
  library = OrderedLibrary ( '/Users/mre/musicage/library.xml' )
  library. usageStats()
  # library. getArtwork()

  return render_to_response('statistics.html', {'library':library, 'DMH': convertToDMH( library.totalTime, 3 )\
    }, context_instance=RequestContext(request))

