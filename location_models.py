# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Court(models.Model):
    court_no = models.PositiveSmallIntegerField(primary_key=True)
    court_name = models.CharField(max_length=50)
    court_address = models.CharField(max_length=100)
    sido_name = models.CharField(max_length=10)
    sigg_name = models.CharField(max_length=10)
    number_3vs3 = models.TextField(db_column='3vs3')  # Field renamed because it wasn't a valid Python identifier. This field type is a guess.
    number_4vs4 = models.TextField(db_column='4vs4')  # Field renamed because it wasn't a valid Python identifier. This field type is a guess.
    number_5vs5 = models.TextField(db_column='5vs5')  # Field renamed because it wasn't a valid Python identifier. This field type is a guess.
    number_6vs6 = models.TextField(db_column='6vs6')  # Field renamed because it wasn't a valid Python identifier. This field type is a guess.
    number_7vs7 = models.TextField(db_column='7vs7')  # Field renamed because it wasn't a valid Python identifier. This field type is a guess.
    number_8vs8 = models.TextField(db_column='8vs8')  # Field renamed because it wasn't a valid Python identifier. This field type is a guess.
    number_9vs9 = models.TextField(db_column='9vs9')  # Field renamed because it wasn't a valid Python identifier. This field type is a guess.
    number_11vs11 = models.TextField(db_column='11vs11')  # Field renamed because it wasn't a valid Python identifier. This field type is a guess.
    cool_heating = models.TextField()  # This field type is a guess.
    cooling = models.TextField()  # This field type is a guess.
    team_vest = models.TextField()  # This field type is a guess.
    training_zone = models.TextField()  # This field type is a guess.
    rent_balls = models.TextField()  # This field type is a guess.
    rent_shoes = models.TextField()  # This field type is a guess.
    shower_room = models.TextField()  # This field type is a guess.
    parking = models.TextField()  # This field type is a guess.

    class Meta:
        managed = False
        db_table = 'court'


class SiggAreas(models.Model):
    sigg_no = models.PositiveSmallIntegerField(primary_key=True)
    adm_code = models.CharField(max_length=10)
    sido_name = models.CharField(max_length=10)
    sigg_name = models.CharField(max_length=10)

    class Meta:
        managed = False
        db_table = 'sigg_areas'
