from django.db import models


class Card(models.Model):
    file_id = models.CharField(max_length=40)

class Deck(models.Model):
    card = models.ForeignKey(Card)
    rank = models.IntegerField()

class Board(models.Model):
    card = models.ForeignKey(Card)
    spot = models.IntegerField()
