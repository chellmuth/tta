import datetime
from django.db import models
from django.contrib.auth.models import User
from django import forms

class OpenGame(models.Model):
    title = models.CharField(max_length=60)
    max_players = models.IntegerField(default=4)
    player_1 = models.ForeignKey(User, blank=True, related_name='player_1_player', null=True)
    player_2 = models.ForeignKey(User, blank=True, related_name='player_2_player', null=True)
    player_3 = models.ForeignKey(User, blank=True, related_name='player_3_player', null=True)
    player_4 = models.ForeignKey(User, blank=True, related_name='player_4_player', null=True)
    date_created = models.DateTimeField(default=datetime.datetime.now)
    date_started = models.DateTimeField(blank=True, null=True)

    def current_players(self):
        count = 1
        for num in range(2, self.max_players + 1):
            attr =  'player_' + str(num)
            if self.__getattribute__(attr):
                count+=1
        return count

class Game(models.Model):
    directory = models.CharField(max_length=40)
    title = models.CharField(max_length=60)
    date_started = models.DateTimeField(default=datetime.datetime.now)
    date_finished = models.DateTimeField(blank=True, null=True)
    date_last_move = models.DateTimeField(blank=True, null=True)

class GamePlayer(models.Model):
    user = models.ForeignKey(User)
    game = models.ForeignKey(Game)

class Heartbeat (models.Model):
    user = models.ForeignKey(User, primary_key=True)
    last_login = models.DateTimeField(default=datetime.datetime.now)

class TTAPasswordInput(forms.PasswordInput):
    class Media:
        css = { 'all': ('/site_media/css/form.css',) }

class LoginForm(forms.Form):
    username = forms.CharField(max_length=100)
    password = forms.CharField(widget=TTAPasswordInput(render_value=False), max_length=100)

class OpenGameForm(forms.ModelForm):
    class Meta:
        model = OpenGame
        fields = ('title', 'max_players')
