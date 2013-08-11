from django.conf.urls import patterns, url, include
from django.views.generic.base import TemplateView
import views

urlpatterns = patterns('',
                       url(r'^create/(?P<request_id>\w+)$', views.create, name='create'),
                       url(r'^view$', views.view_your, name='view_your'),
                       url(r'^view/(?P<id_response>\w+)$', views.view_id, name='view_your_id'),
                       url(r'^edit/(?P<id_response>\w+)$', views.edit_id, name='edit'),
                       url(r'^buy/(?P<id_response>\w+)$', views.buy, name='buy'),
                       url(r'^collect/(?P<id_response>\w+)$', views.collect, name='collect'),
)