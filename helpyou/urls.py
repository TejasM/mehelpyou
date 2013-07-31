from django.core.urlresolvers import reverse
from django.views.generic.base import RedirectView
from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
import userprofile

admin.autodiscover()

urlpatterns = patterns('',
                       url(r'^$', TemplateView.as_view(template_name="base.html")),

                       # Examples:
                       # url(r'^$', 'mehelpyou.views.home', name='home'),
                       url(r'^users/', include('helpyou.userprofile.urls', namespace='user')),
                       url(r'^request/', include('helpyou.request.urls', namespace='request')),
                       url(r'^response/', include('helpyou.response.urls', namespace='response')),
                       url(r'', include('social_auth.urls')),
                       # Uncomment the admin/doc line below to enable admin documentation:
                       # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

                       # Uncomment the next line to enable the admin:
                       url(r'^admin/', include(admin.site.urls)),
)
