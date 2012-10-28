from django.http import HttpResponse, HttpResponseForbidden, HttpResponseServerError, HttpResponseRedirect
from django.shortcuts import render, render_to_response
from django.template import RequestContext
import settings
import os, sys, pdb
from library.Librarian import Librarian
from backend.forms  import LibraryForm

#cross site forgery exempt
from django.views.decorators.csrf import csrf_exempt

def home(request):
  if not request.user.is_authenticated():
    return HttpResponseRedirect("/login/")
  if not request.user.get_profile().has_library:
    return HttpResponseRedirect("/upload_library/")

  librarian = Librarian ( request.user.library )
  # librarian. createEntries()

  return HttpResponseRedirect("/statistics/")

def statistics(request):
  if not request.user.is_authenticated():
    return HttpResponseRedirect("/login/")
  if not request.user.get_profile().has_library:
    return HttpResponseRedirect("/upload_library/")

  librarian = Librarian ( request.user.library )
  librarian. usageStats()
  
  return render_to_response('statistics.html', {'library':librarian }, \
      context_instance=RequestContext(request))

def topListen(request):
  if not request.user.is_authenticated():
    return HttpResponseRedirect("/login/")

  try:
    toShow = int(request.GET.get('toShow').rstrip('/'))
  except AttributeError:
    toShow = 10
  except ValueError:
    toShow = 10

  print toShow
  if toShow < 10:
    toShow = 10
  librarian = Librarian ( request.user.library )
  librarian. generateLists( toShow )

  return render_to_response('artists.html', {'library':librarian, 'toShow':toShow+10}, \
      context_instance=RequestContext(request))

def browseLibrary( request ):
  if not request.user.is_authenticated():
    return HttpResponseRedirect("/login/")

  librarian = Librarian ( request.user.library )
  found = librarian. getRequest( request.path )
  print found
  if found == None:
    sys.stderr.write("Page not found, at %s\n" % request.path)

  return render_to_response('browse.html', {'found': found[0] }, \
      context_instance=RequestContext(request))

@csrf_exempt
def upload_library(request):
  if not request.user.is_authenticated():
    return HttpResponseRedirect("/login/")
  
  # setup user or removes old library
  if not request.user.has_library:
    request.user.get_profile().setup_user()
    request.user.get_profile().save()
  else:
    try:
      os.remove( request.user.library )
    except OSError:
      sys.stderr.write("Could not remove file: %s\n" % request.user.library )
      
  if request.method == 'POST':
    form = LibraryForm(request.POST, request.FILES)
    if form.is_valid():
      print "valid form"
      handle_uploaded_file(request.FILES['library'], request.user.itunes_library)

      librarian = Librarian ( request.user.library )
      librarian. addSongsfromXML( request.user.itunes_library )

      return HttpResponseRedirect('/statistics/')
    print "INVALID FORM"
  else:
    print "GET METHOD"
    form = LibraryForm()

  return render_to_response('upload_library.html', {'form': form},
      context_instance=RequestContext(request))

def handle_uploaded_file(f, dst):
  print " loading file"
  with open( dst, 'wb+') as destination:
    for chunk in f.chunks():
        destination.write(chunk)
