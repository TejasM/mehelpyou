from django.conf.urls import patterns, url
import views

urlpatterns = patterns('',
                       url(r'^$', views.index, name='index'),
                       url(r'^login$', views.loginUser, name='login'),
                       url(r'^logout$', views.logout_view, name='logout'),
                       url(r'^signup$', views.signup, name='signup'),
                       url(r'^(?P<user_id>\d+)$', views.user_view, name='user'),
                       url(r'^collect/$', views.collect, name='collect'),
                       url(r'^send_invite/$', views.invite_connection, name='invite'),
                       url(r'^accept_invite/$', views.accept_connection, name='accept'),
                       url(r'^send_user_invites/$', views.send_user_invites, name='send_user_invites'),
                       url(r'^buy_points/$', views.buy_points, name='buy_points'),
                       url(r'^pricing/$', views.pricing, name='pricing'),
                       url(r'^change_pic/$', views.change_pic, name='change_pic'),
                       url(r'^web_hook/$', views.web_hook, name='web_hook'),
)