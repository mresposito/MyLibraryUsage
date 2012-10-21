from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
import settings

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()
urlpatterns = patterns('',
    # Examples:
     url(r'^$', 'settings.views.home', name='home'),
     url(r'^upload_file/$', 'settings.views.upload_file', name='this_file'),
     url(r'^statistics/$', 'settings.views.statistics', name='statistics'),
     url(r'^artists/$', 'settings.views.artists', name='artists'),
   # url(r'^mre/', include('mre.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
    (r'^static/(?P<path>.*html)$', 'django.views.static.serve',{'document_root': settings.MEDIA_ROOT,'show_indexes' : True}),
    (r'^static/(?P<path>.*css)$', 'django.views.static.serve',{'document_root': settings.MEDIA_ROOT,'show_indexes' : True}),
    (r'^static/(?P<path>.*jpg)$', 'django.views.static.serve',{'document_root': settings.MEDIA_ROOT,'show_indexes' : True}),
    (r'^static/(?P<path>.*png)$', 'django.views.static.serve',{'document_root': settings.MEDIA_ROOT,'show_indexes' : True}),
    (r'^static/(?P<path>.*otf)$', 'django.views.static.serve',{'document_root': settings.MEDIA_ROOT,'show_indexes' : True}),
    (r'^static/(?P<path>.*pdf)$', 'django.views.static.serve',{'document_root': settings.MEDIA_ROOT,'show_indexes' : True}),
    (r'^static/(?P<path>.*js)$', 'django.views.static.serve',{'document_root': settings.MEDIA_ROOT,'show_indexes' : True}),
)
