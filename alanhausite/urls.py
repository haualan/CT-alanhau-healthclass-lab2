from django.conf.urls import patterns, include, url
from django.contrib import admin

# from NLPscore import views
from main import views

urlpatterns = patterns('',
    # Examples:

    url(r'^$', include('main.urls', namespace="main")),
    url(r'^resume', views.exportResumeFile, name="resume"),
    url(r'^NLPscore/', include('NLPscore.urls', namespace="NLPscore")),


    # disable admin for now
    # url(r'^admin/', include(admin.site.urls))
)
