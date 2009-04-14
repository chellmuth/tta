from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^tta/', include('tta.foo.urls')),

    (r'^(\w+)/card_row/$', 'tta.game.views.index'),
    (r'^(\w+)/slide/$', 'tta.game.views.slide'),
    (r'^(\w+)/undo/$', 'tta.game.views.undo'),
    (r'^(\w+)/play/(\d+)/$', 'tta.game.views.play'),
    (r'^(\w+)/add/(\d+)$', 'tta.game.views.add_to_hand'),
    (r'^(\w+)/begin/$', 'tta.game.views.begin'),
    (r'^(\w+)/save/$', 'tta.game.views.save'),
    (r'^(\w+)/reset/$', 'tta.game.views.reset'),
    (r'^remove_card/(\d+)$', 'tta.game.views.remove_card'),
    (r'^site_media/(?P<path>.*$)', 'django.views.static.serve',
             {'document_root': '/home/cjh/projects/tta/media'}),
    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # (r'^admin/', include(admin.site.urls)),
)
