from django.conf.urls import patterns, url
import views

urlpatterns = patterns('',
                       url(r'^contact$', views.contact, name='contact'),
)