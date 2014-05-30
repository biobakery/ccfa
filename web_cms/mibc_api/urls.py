"""MIBC web API urls."""
from django.conf.urls import patterns, url
from django.views.generic.base import RedirectView
from django.contrib.auth.decorators import login_required

from . import (
    views
)

urlpatterns = patterns(
    'mibc_api.views',
    url(r'^users$', login_required(views.users_all), 
        name="mibc_api_users_all",),
    url(r'^projects/(?P<username>.*)/(?P<projectname>.*)/validate/?$', 
        login_required(views.validate_project), 
        name="mibc_api_validate_project",),
    url(r'^projects/(?P<username>.*)/(?P<projectname>.*)/mapvalidate$', 
        login_required(views.mapvalidate_project), 
        name="mibc_api_mapvalidate_project",),
    url(r'^projects/(?P<username>.*)/(?P<projectname>.*)$', 
        login_required(views.project), 
        name="mibc_api_project",),
    url(r'^users/(?P<name>.*)$', login_required(views.user), 
        name="mibc_api_user",),
    url(r'^utilities/efovalidate$', views.efovalidate, 
        name="mibc_api_efovalidate",),
    url(r'^utilities/efosuggest$', views.efosuggest, 
        name="mibc_api_efosuggest",),
    url(r'^utilities/upload_file/(?P<path>.*)/?$', 
        login_required(views.upload_file), 
        name="mibc_api_upload_file",)
)
