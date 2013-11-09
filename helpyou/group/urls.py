from django.conf.urls import patterns, url, include
from django.views.generic.base import TemplateView
import views

urlpatterns = patterns('',
                       url(r'^(?P<group_id>\d+)$', views.index, name='index'),
                       url(r'^your$', views.list_your, name='list'),
                       url(r'^create$', views.create, name='create'),
                       url(r'^add/(?P<group_id>\d+)$', views.add_to_group, name='add'),
                       url(r'^remove/(?P<group_id>\d+)$', views.remove_from_group, name='remove'),
                       url(r'^addtoadmin/(?P<group_id>\d+)$', views.move_to_administrators, name='move'),
                       url(r'^edit/(?P<group_id>\d+)$', views.edit, name='edit'),
                       url(r'^join/(?P<group_id>\d+)$', views.request_invitation, name='join'),
)