from django.db.models.signals import post_save
from django.db import models
from django.contrib.auth.models import User

import settings
import random, os, string
     
class UserProfile(models.Model):
  has_library  = models.BooleanField( default=False )
  library_id   = models.CharField   ( max_length = 30 )
  library_path = models.CharField   ( max_length = 60 )

  user = models.ForeignKey(User, unique=True) 
  
  def setup_user( self ):
    if self. has_library: # sanity check
      return
    unique = create_id()
    self.library_id = unique
    self. has_library = True

    dir_path =  os.path.join(settings.LIB_DIR,  unique )
    if not os.path.exists( dir_path ):
      os.makedirs( dir_path ) 

    self.library_path = os.path.join( dir_path, unique ) +".db"

  def get_itunes_library ( self ):
    return self.library_path.replace( "db", "xml" )

def create_id():
  return ''.join(random.choice(string.letters+ string.digits) for x in range(30))

def create_user_profile(sender, instance, created, **kwargs):
  if created:
    UserProfile.objects.create(user=instance)

post_save.connect(create_user_profile, sender=User)

User.profile        = property(lambda u: u.get_profile() )
User.library        = property(lambda u: u.get_profile().library_path )
User.itunes_library = property(lambda u: u.get_profile().get_itunes_library() )
User.has_library    = property(lambda u: u.get_profile().has_library  )
