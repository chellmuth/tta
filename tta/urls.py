from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^tta/', include('tta.foo.urls')),

    (r'^card_row/$', 'tta.game.views.index'),
    (r'^remove_card/(\d+)$', 'tta.game.views.remove_card'),
    (r'^site_media/(?P<path>.*$)', 'django.views.static.serve',
             {'document_root': '/home/cjh/projects/tta/media'}),
    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # (r'^admin/', include(admin.site.urls)),
)
