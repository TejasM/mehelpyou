from django.conf.urls import patterns, url
import views

urlpatterns = patterns('',
                       url(r'^$', views.notifications, name='index'),
                       url(r'^view/(?P<id_notification>\w+)$', views.view_notification, name='view'),
)