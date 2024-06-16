from django.conf import settings
from django.db import models
from django.contrib.auth.models import Group


class Court(models.Model):
    court_no = models.PositiveSmallIntegerField(primary_key=True)
    court_name = models.CharField(max_length=50)
    court_address = models.CharField(max_length=100)
    sido_name = models.CharField(max_length=10)
    sigg_name = models.CharField(max_length=10)
    number_3vs3 = models.TextField(
        db_column="3vs3"
    )  # Field renamed because it wasn't a valid Python identifier. This field type is a guess.
    number_4vs4 = models.TextField(
        db_column="4vs4"
    )  # Field renamed because it wasn't a valid Python identifier. This field type is a guess.
    number_5vs5 = models.TextField(
        db_column="5vs5"
    )  # Field renamed because it wasn't a valid Python identifier. This field type is a guess.
    number_6vs6 = models.TextField(
        db_column="6vs6"
    )  # Field renamed because it wasn't a valid Python identifier. This field type is a guess.
    number_7vs7 = models.TextField(
        db_column="7vs7"
    )  # Field renamed because it wasn't a valid Python identifier. This field type is a guess.
    number_8vs8 = models.TextField(
        db_column="8vs8"
    )  # Field renamed because it wasn't a valid Python identifier. This field type is a guess.
    number_9vs9 = models.TextField(
        db_column="9vs9"
    )  # Field renamed because it wasn't a valid Python identifier. This field type is a guess.
    number_11vs11 = models.TextField(
        db_column="11vs11"
    )  # Field renamed because it wasn't a valid Python identifier. This field type is a guess.
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
        db_table = "court"


class Team(models.Model):
    team_no = models.AutoField(primary_key=True)
    team_name = models.CharField(unique=True, max_length=10)
    team_image_url = models.ImageField(blank=True, null=True)
    team_day = models.CharField(max_length=15)
    team_timeslot = models.CharField(max_length=10)
    team_ages = models.CharField(max_length=10)
    GENDER_CHOICES = [
        ("여성", "여성"),
        ("남성", "남성"),
        ("혼성", "혼성"),
    ]
    gender = models.CharField(
        max_length=2, choices=GENDER_CHOICES, null=True, blank=True
    )
    team_level = models.IntegerField(null=True, blank=True)
    create_date = models.DateTimeField(auto_now_add=True)
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="teams", blank=True
    )
    # 팀장 지정
    created_by = models.OneToOneField(
        settings.AUTH_USER_MODEL, related_name="created_team", on_delete=models.CASCADE
    )
    sido_name = models.CharField(max_length=10)
    sigg_name = models.CharField(max_length=10)
    court_name = models.CharField(max_length=50)

    class Meta:
        managed = True
        db_table = "team"

    def __str__(self):
        return self.team_name

    def get_members_usernames(self):
        return ", ".join([member.username for member in self.members.all()])

    def is_leader(self, user):
        return self.created_by == user
