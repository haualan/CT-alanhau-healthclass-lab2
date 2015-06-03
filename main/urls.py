from django.conf.urls import patterns, url

from main import views

urlpatterns = patterns('',
  url(r'^$', views.MainIndexView.as_view(), name='index'),
  url(r'^resume$', views.exportResumeFile, name='resume'),

  
)