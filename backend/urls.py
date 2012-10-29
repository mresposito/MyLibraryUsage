from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()
urlpatterns = patterns('',
    # Examples:
   url(r'^$'                , 'backend.views.home'           , name='home')           ,
   url(r'^/$'               , 'backend.views.home'           , name='home')           ,
   url(r'^home/$'           , 'backend.views.home'           , name='home')           ,
   url(r'^upload_library/$' , 'backend.views.upload_library' , name='uploadXML')      ,
   url(r'^statistics/$'     , 'backend.views.statistics'     , name='statistics')     ,
   url(r'^top_listen/$'     , 'backend.views.topListen'      , name='topListen')      ,
   url(r'^song_[0-9]+/$'    , 'backend.views.browseLibrary'  , name='browsingSystem') ,
   url(r'^album_[0-9]+/$'   , 'backend.views.browseLibrary'  , name='browsingSystem') ,
   url(r'^artist_[0-9]+/$'  , 'backend.views.browseLibrary'  , name='browsingSystem') ,
   url(r'^genre_[0-9]+/$'   , 'backend.views.browseLibrary'  , name='browsingSystem') ,

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^login/$', 'django.contrib.auth.views.login'),
    url(r'^logout/$', 'django.contrib.auth.views.logout', {'next_page': '/'}),
    url(r'^password_change/$', 'django.contrib.auth.views.password_change',{'post_change_redirect': '/start/'}),
    url(r'^password_change_done/$', 'django.contrib.auth.views.password_change_done'),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    # file stuff
    (r'^static/(?P<path>.*html)$', 'django.views.static.serve',{'document_root': settings.MEDIA_ROOT,'show_indexes' : True}),
    (r'^static/(?P<path>.*css)$', 'django.views.static.serve',{'document_root': settings.MEDIA_ROOT,'show_indexes' : True}),
    (r'^static/(?P<path>.*jpg)$', 'django.views.static.serve',{'document_root': settings.MEDIA_ROOT,'show_indexes' : True}),
    (r'^static/(?P<path>.*png)$', 'django.views.static.serve',{'document_root': settings.MEDIA_ROOT,'show_indexes' : True}),
    (r'^static/(?P<path>.*js)$', 'django.views.static.serve',{'document_root': settings.MEDIA_ROOT,'show_indexes' : True}),
)
