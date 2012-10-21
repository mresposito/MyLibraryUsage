import time, uuid
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseServerError, HttpResponseRedirect
from django.shortcuts import render, render_to_response
from django.template import RequestContext
import settings, os
from Library import Library
from model   import UploadFileForm

def home(request):
  library = Library ( 'tmp/database.db' )
  library. addItunesLibrary(os.path.join(settings.PROJECT_DIR,'library.xml' ))

  return render_to_response('home.html', {'library':library },\
      context_instance=RequestContext(request))

def statistics(request):
  library = Library ( 'tmp/database.db' )
  library. usageStats()
  # library. generateChar()

  return render_to_response('statistics.html', {'library':library },\
      context_instance=RequestContext(request))

def artists(request):
  library = Library ( 'tmp/database.db' )
  # library. usageStats()
  t1 = time.time()
  library. artistStats()
  library.  albumStats()
  library.  genreStats()
  t2 = time.time()
  print 'took %0.3f ms' %  (t2-t1)
  library. findArtwork()

  return render_to_response('artists.html', {'library':library },\
      context_instance=RequestContext(request))

def upload_file(request):
  print "uploading"
  if request.method == 'POST':
      xml = request.POST['xml']
      form = UploadFileForm( xml, request.FILES)
      if form.is_valid():
        # userLibrary
          handle_uploaded_file(request.FILES['file'])
          return HttpResponseRedirect('/statistics/')
  else:
      form = UploadFileForm()

  return render_to_response('statistics.html', {'database': 303})

def handle_uploaded_file(f):
  with open('tmp/database.db', 'wb+') as destination:
      for chunk in f.chunks():
          destination.write(chunk)
  print " loading file"
  library = Library ( 'tmp/database.db' )
  library. addItunesLibrary(os.path.join(settings.PROJECT_DIR,'library.xml' ))
