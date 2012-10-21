#!/usr/bin/env python
# coding: utf-8
""" declaration of user model """

###      @file:  model.py
###
###    @author:  Michele Esposito
###    Company:  myself!

from django import forms
from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum
from django.conf import settings

class UploadFileForm( forms.Form ):
  title = forms.CharField()
  file  = forms.FileField(  )

# Imaginary function to handle an uploaded file.
