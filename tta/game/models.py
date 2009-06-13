import datetime
from django.db import models
from django.contrib.auth.models import User

class Heartbeat (models.Model):
    user = models.ForeignKey(User, primary_key=True)
    last_login = models.DateTimeField(default=datetime.datetime.now)
