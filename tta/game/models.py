import datetime
from django.db import models
from django.contrib.auth.models import User
from django import forms

class Game(models.Model):
    directory = models.CharField(max_length=40)
    title = models.CharField(max_length=60)
    date_started = models.DateTimeField(default=datetime.datetime.now)
    date_finished = models.DateTimeField(default=datetime.datetime.now)
    date_last_move = models.DateTimeField(default=datetime.datetime.now)
    winner = models.ForeignKey(User)

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
