from django.conf.urls import patterns, url

from energymon_app import views

urlpatterns = patterns('',
                       url(r'^$', views.index, name='index'),
                       url(r'^gen', views.gen, name='gen'),
                      )
