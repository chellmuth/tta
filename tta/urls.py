from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^tta/', include('tta.foo.urls')),

    (r'^(\w+)/(\w+)/card_row/$', 'tta.game.views.index'),
    (r'^(\w+)/(\w+)/slide/$', 'tta.game.views.slide'),
    (r'^(\w+)/(\w+)/undo/$', 'tta.game.views.undo'),
    (r'^(\w+)/(\w+)/play/(\d+)/$', 'tta.game.views.play'),
    (r'^(\w+)/(\w+)/play_event/(\d+)/$', 'tta.game.views.play_event'),
    (r'^(\w+)/(\w+)/add/(\d+)$', 'tta.game.views.add_to_hand'),
    (r'^(\w+)/(\w+)/begin/$', 'tta.game.views.begin'),
    (r'^(\w+)/(\w+)/save/$', 'tta.game.views.save'),
    (r'^(\w+)/(\w+)/reset/$', 'tta.game.views.reset'),
    (r'^(\w+)/(\w+)/blue_cell_up/(\w+)/$', 'tta.game.views.blue_cell_up'),
    (r'^(\w+)/(\w+)/blue_cell_down/(\w+)/$', 'tta.game.views.blue_cell_down'),
    (r'^(\w+)/(\w+)/count_up/(\w+)/$', 'tta.game.views.count_up'),
    (r'^(\w+)/(\w+)/count_down/(\w+)/$', 'tta.game.views.count_down'),
    (r'^(\w+)/(\w+)/yellow_up/(\w+)/$', 'tta.game.views.yellow_up'),
    (r'^(\w+)/(\w+)/yellow_down/(\w+)/$', 'tta.game.views.yellow_down'),
    (r'^(\w+)/(\w+)/points_up/(\w+)/$', 'tta.game.views.points_up'),
    (r'^(\w+)/(\w+)/points_down/(\w+)/$', 'tta.game.views.points_down'),
    (r'^(\w+)/(\w+)/draw_military/(\w+)/$', 'tta.game.views.draw_military'),
    (r'^(\w+)/(\w+)/pop_current_event/$', 'tta.game.views.pop_current_event'),
    (r'^remove_card/(\d+)$', 'tta.game.views.remove_card'),
    (r'^site_media/(?P<path>.*$)', 'django.views.static.serve',
             {'document_root': '/home/cjh/projects/tta/media'}),
    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # (r'^admin/', include(admin.site.urls)),
)
