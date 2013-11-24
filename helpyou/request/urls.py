from django.conf.urls import patterns, url, include
from django.views.generic.base import TemplateView
import views

urlpatterns = patterns('',
                       url(r'^create$', views.create, name='create'),
                       url(r'^view$', views.view_your, name='view_your'),
                       url(r'^view/all$', views.view_all, name='view_all'),
                       url(r'^view/connections$', views.view_connections, name='view_connections'),
                       url(r'^view/(?P<id_request>\w+)$', views.view_id, name='view_your_id'),
                       url(r'^edit/(?P<id_request>\w+)$', views.edit_id, name='edit'),
                       url(r'^clarify/(?P<id_request>\w+)$', views.ask_clarification, name='clarify'),
                       url(r'^clarify_answer/(?P<id_request>\w+)$', views.answer_clarification, name='clarify_answer'),
)