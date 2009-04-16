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
    (r'^(\w+)/play_event/(\d+)/$', 'tta.game.views.play_event'),
    (r'^(\w+)/add/(\d+)$', 'tta.game.views.add_to_hand'),
    (r'^(\w+)/begin/$', 'tta.game.views.begin'),
    (r'^(\w+)/save/$', 'tta.game.views.save'),
    (r'^(\w+)/reset/$', 'tta.game.views.reset'),
    (r'^(\w+)/blue_cell_up/(\w+)/$', 'tta.game.views.blue_cell_up'),
    (r'^(\w+)/blue_cell_down/(\w+)/$', 'tta.game.views.blue_cell_down'),
    (r'^(\w+)/count_up/(\w+)/$', 'tta.game.views.count_up'),
    (r'^(\w+)/count_down/(\w+)/$', 'tta.game.views.count_down'),
    (r'^(\w+)/yellow_up/(\w+)/$', 'tta.game.views.yellow_up'),
    (r'^(\w+)/yellow_down/(\w+)/$', 'tta.game.views.yellow_down'),
    (r'^(\w+)/points_up/(\w+)/$', 'tta.game.views.points_up'),
    (r'^(\w+)/points_down/(\w+)/$', 'tta.game.views.points_down'),
    (r'^(\w+)/draw_military/(\w+)/$', 'tta.game.views.draw_military'),
    (r'^remove_card/(\d+)$', 'tta.game.views.remove_card'),
    (r'^site_media/(?P<path>.*$)', 'django.views.static.serve',
             {'document_root': '/home/cjh/projects/tta/media'}),
    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # (r'^admin/', include(admin.site.urls)),
)
