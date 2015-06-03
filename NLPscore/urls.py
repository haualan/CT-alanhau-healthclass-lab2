from django.conf.urls import patterns, url

from NLPscore import views

urlpatterns = patterns('',

  url(r'^$', views.docScoreView.as_view(), name='docScore'),

)

