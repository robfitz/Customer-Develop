from django.conf.urls.defaults import *

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    (r'^$', 'mycd.views.index'),
    (r'^scrap/', 'mycd.views.scrap'),
    (r'^export/', 'mycd.views.export'),
    (r'^import/', 'mycd.views.importCsv'),
    (r'^login/', 'mycd.views.login'),
    (r'^register/', 'mycd.views.register'),
    (r'^logout/', 'mycd.views.signout'),
    (r'^dashboard/', 'mycd.views.dashboard'),
    (r'^contacts/(?P<contact_id>\d+)/$', 'mycd.views.editContact'),
    (r'^contacts/', 'mycd.views.contactList'),
    (r'^worksheet/(?P<worksheet_id>\d+)/$', 'mycd.views.worksheet'),
    (r'^admin/', include(admin.site.urls)),
    (r'^assets/(?P<path>.*)$', 'django.views.static.serve', {'document_root': 'C:/www/customerdev/assets'}),
)
