from django.conf.urls import patterns, url

urlpatterns = patterns('helpyou.avatar.views',
    url('^change/$', 'change', name='avatar_change'),
    url('^delete/$', 'delete', name='avatar_delete'),
)
