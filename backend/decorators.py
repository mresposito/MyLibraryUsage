#!/usr/bin/env python
# coding: utf-8
""" main file """

def has_library( fun ):
  def wrapper(*args, **kwargs):
    if not args[0].user.get_profile().has_library:
      return HttpResponseRedirect('/upload_library/')

    return fun( *args, **kwargs )
  return wrapper

