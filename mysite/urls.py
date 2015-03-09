from django.conf.urls import patterns, include, url
from django.contrib import admin

from polls import views

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'mysite.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^polls/', include('polls.urls', namespace="polls")),
    url(r'^callback$', views.callback, name='callback'),
    url(r'^admin/', include(admin.site.urls)),
)
