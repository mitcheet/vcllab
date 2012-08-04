from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('lab.views',
	url(r'^$', 'index'),
	url(r'^logout/', 'logout_view'),
    # Examples:
    # url(r'^$', 'vcl.views.home', name='home'),
    # url(r'^vcl/', include('vcl.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
