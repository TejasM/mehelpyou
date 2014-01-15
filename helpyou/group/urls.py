from django.conf.urls import patterns, url, include
from django.views.generic.base import TemplateView
import views

urlpatterns = patterns('',
                       url(r'^(?P<group_id>\d+)$', views.index, name='index'),
                       url(r'^your$', views.list_your, name='list'),
                       url(r'^create$', views.create, name='create'),
                       url(r'^add/(?P<group_id>\d+)$', views.add_to_group, name='add'),
                       url(r'^edit/(?P<group_id>\d+)$', views.edit, name='edit'),
)