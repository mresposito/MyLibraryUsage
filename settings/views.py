import time, uuid
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseServerError, HttpResponseRedirect
from django.shortcuts import render, render_to_response
from django.template import RequestContext
import settings
from musicImport import *

def home(request):

  return render_to_response('home.html',{},context_instance=RequestContext(request))

def statistics(request):
  library = Library (os.path.join(settings.PROJECT_DIR,'library.xml' ))
  library. usageStats()

  return render_to_response('statistics.html', {'library':library, 'DMH': convertToDMH( library.totalTime, 3 )\
    }, context_instance=RequestContext(request))

