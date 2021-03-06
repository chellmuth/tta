from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^tta/', include('tta.foo.urls')),

    (r'^$', 'tta.game.views.home'),
    (r'^(\w+)/(\w+)/(\d+)/card_row/$', 'tta.game.views.index'),
    (r'^(\w+)/(\w+)/(\w+)/slide/$', 'tta.game.views.slide'),
    (r'^(\w+)/(\w+)/(\w+)/undo/$', 'tta.game.views.undo'),
    (r'^(\w+)/(\w+)/(\w+)/play/(\d+)/$', 'tta.game.views.play'),
    (r'^(\w+)/(\w+)/(\w+)/discard/(\d+)/$', 'tta.game.views.discard'),
    (r'^(\w+)/(\w+)/(\w+)/discard_leader/$', 'tta.game.views.discard_leader'),
    (r'^(\w+)/(\w+)/(\w+)/play_event/(\d+)/$', 'tta.game.views.play_event'),
    (r'^(\w+)/(\w+)/(\w+)/play_aggression/(\d+)/$', 'tta.game.views.play_aggression'),
    (r'^(\w+)/(\w+)/(\w+)/play_pact/(\d+)/$', 'tta.game.views.play_pact'),
    (r'^(\w+)/(\w+)/(\w+)/remove_aggression/(\d+)/$', 'tta.game.views.remove_aggression'),
    (r'^(\w+)/(\w+)/(\w+)/remove_pact/(\d+)/$', 'tta.game.views.remove_pact'),
    (r'^(\w+)/(\w+)/(\w+)/add/(\d+)$', 'tta.game.views.add_to_hand'),
    (r'^(\w+)/(\w+)/(\w+)/begin/$', 'tta.game.views.begin'),
    (r'^(\w+)/(\w+)/(\w+)/save/$', 'tta.game.views.save'),
    (r'^(\w+)/(\w+)/(\w+)/reset/$', 'tta.game.views.reset'),
    (r'^(\w+)/(\w+)/(\w+)/blue_cell_up/(\w+)/$', 'tta.game.views.blue_cell_up'),
    (r'^(\w+)/(\w+)/(\w+)/blue_cell_down/(\w+)/$', 'tta.game.views.blue_cell_down'),
    (r'^(\w+)/(\w+)/(\w+)/count_up/(\w+)/$', 'tta.game.views.count_up'),
    (r'^(\w+)/(\w+)/(\w+)/count_down/(\w+)/$', 'tta.game.views.count_down'),
    (r'^(\w+)/(\w+)/(\w+)/yellow_up/(\w+)/$', 'tta.game.views.yellow_up'),
    (r'^(\w+)/(\w+)/(\w+)/yellow_down/(\w+)/$', 'tta.game.views.yellow_down'),
    (r'^(\w+)/(\w+)/(\w+)/points_up/(\w+)/$', 'tta.game.views.points_up'),
    (r'^(\w+)/(\w+)/(\w+)/points_down/(\w+)/$', 'tta.game.views.points_down'),
    (r'^(\w+)/(\w+)/(\w+)/draw_military/(\w+)/$', 'tta.game.views.draw_military'),
    (r'^(\w+)/(\w+)/(\w+)/pop_current_event/$', 'tta.game.views.pop_current_event'),
    (r'^(\w+)/(\w+)/(\w+)/take_territory/$', 'tta.game.views.take_territory'),
    (r'^(\w+)/(\w+)/(\w+)/finish_wonder/$', 'tta.game.views.finish_wonder'),
    (r'^(\w+)/(\w+)/stuff/$', 'tta.game.views.stuff'),
    (r'^login/$', 'tta.game.views.login'),
    (r'^account/login/$', 'tta.game.views.login'),
    (r'^logout/$', 'tta.game.views.logout'),
    (r'^heartbeat/(\w+)/(\w+)/(\w+)/$', 'tta.game.views.heartbeat'),
    (r'^profile/(\d+)(?:/\w+)?/$', 'tta.game.views.profile'),
    (r'^register/$', 'tta.game.views.register'),
    (r'^open/create/$', 'tta.game.views.create_game'),
    (r'^open/show/(\d+)/$', 'tta.game.views.show_game'),
    (r'^open/join/(\d+)/$', 'tta.game.views.join_game'),
    (r'^open/list/$', 'tta.game.views.list_games'),
    (r'^open/start/$', 'tta.game.views.start_game'),
    (r'^site_media/(?P<path>.*$)', 'django.views.static.serve',
     {'document_root': '/home/cjh/projects/tta/media'}),
    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # (r'^admin/', include(admin.site.urls)),
)
