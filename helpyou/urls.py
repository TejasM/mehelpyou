from django.core.urlresolvers import reverse
from django.views.generic.base import RedirectView
from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from views import index, about, reset_confirm, reset

from django.conf import settings
from django.conf.urls.static import static

admin.autodiscover()

urlpatterns = patterns('',
                       url(r'^$', view=index, name='index'),
                       url(r'^alt/$', view=TemplateView.as_view(template_name='base-home-alt.html')),
                       url(r'^reset/confirm/(?P<uidb36>[0-9A-Za-z]+)/$',
                           reset_confirm, name='reset_confirm'),
                       url(r'^reset/$', reset, name='reset'),
                       url(r'^terms/$', view=TemplateView.as_view(template_name='terms.html')),
                       url(r'^privacy/$', view=TemplateView.as_view(template_name='privacy.html')),
                       url(r'^about/$', view=about),  # Examples:
                       # url(r'^$', 'mehelpyou.views.home', name='home'),
                       url(r'^users/', include('helpyou.userprofile.urls', namespace='user')),
                       url(r'^groups/', include('helpyou.group.urls', namespace='group')),
                       url(r'^request/', include('helpyou.request.urls', namespace='request')),
                       url(r'^response/', include('helpyou.response.urls', namespace='response')),
                       url(r'^index/', include('helpyou.index.urls', namespace='index')),
                       url(r'', include('social_auth.urls')),
                       url(r"^payments/", include("payments.urls")),
                       url(r'^notifications/', include('helpyou.notifications.urls', namespace='notifications')),
                       # Uncomment the admin/doc line below to enable admin documentation:
                       # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
                       url(r'^avatars/(?P<path>.*)$',
                           'django.views.static.serve',
                           {'document_root': settings.MEDIA_ROOT, }),
                       # Uncomment the next line to enable the admin:
                       url(r'^admin/', include(admin.site.urls)),
                       url(r'^tz-detect/', include('tz_detect.urls')),
)