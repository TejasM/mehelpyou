from django.conf.urls import patterns, url, include
from django.views.generic.base import TemplateView
import views

urlpatterns = patterns('',
                       url(r'^$', views.index, name='index'),
                       url(r'^login$', views.loginUser, name='login'),
                       url(r'^logout$', views.logout_view, name='logout'),
                       url(r'^signup$', views.signup, name='signup'),
                       url(r'^(?P<username>\w+)$', views.user_view, name='user'),
)