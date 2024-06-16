# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class FaTeam(models.Model):
    team_no = models.PositiveIntegerField(primary_key=True)
    team_name = models.CharField(unique=True, max_length=10)
    team_image_url = models.CharField(max_length=248, blank=True, null=True)
    team_day = models.CharField(max_length=15)
    team_timeslot = models.CharField(max_length=10)
    activity_area_no = models.PositiveSmallIntegerField()
    activity_court_no = models.PositiveSmallIntegerField()
    team_ages = models.CharField(max_length=10)
    team_sex = models.CharField(max_length=10)
    team_level = models.CharField(max_length=10, blank=True, null=True)
    create_date = models.DateTimeField()
    update_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'fa_team'


class Match(models.Model):
    match_no = models.PositiveIntegerField(primary_key=True)
    team_no_1 = models.ForeignKey(FaTeam, models.DO_NOTHING, db_column='team_no_1')
    team_no_2 = models.ForeignKey(FaTeam, models.DO_NOTHING, db_column='team_no_2', related_name='match_team_no_2_set', blank=True, null=True)
    match_date = models.DateField()
    match_area_no = models.PositiveSmallIntegerField()
    match_court_no = models.PositiveSmallIntegerField()
    match_start_time = models.CharField(max_length=10)
    match_end_time = models.CharField(max_length=10)
    match_sex = models.CharField(max_length=10)
    match_level = models.CharField(max_length=10, blank=True, null=True)
    match_number = models.CharField(max_length=5)
    status = models.CharField(max_length=5)

    class Meta:
        managed = False
        db_table = 'match'


class MatchResult(models.Model):
    match_no = models.OneToOneField(Match, models.DO_NOTHING, db_column='match_no', primary_key=True)
    team_no_1 = models.ForeignKey(FaTeam, models.DO_NOTHING, db_column='team_no_1')
    team_no_2 = models.ForeignKey(FaTeam, models.DO_NOTHING, db_column='team_no_2', related_name='matchresult_team_no_2_set')
    team_1_quarter_1 = models.PositiveIntegerField(blank=True, null=True)
    team_1_quarter_2 = models.PositiveIntegerField(blank=True, null=True)
    team_1_quarter_3 = models.PositiveIntegerField(blank=True, null=True)
    team_1_quarter_4 = models.PositiveIntegerField(blank=True, null=True)
    team_1_win = models.PositiveIntegerField(blank=True, null=True)
    team_1_draw = models.PositiveIntegerField(blank=True, null=True)
    team_1_lose = models.PositiveIntegerField(blank=True, null=True)
    team_1_goal_score = models.IntegerField(blank=True, null=True)
    team_1_points = models.PositiveIntegerField(blank=True, null=True)
    team_2_quarter_1 = models.PositiveIntegerField(blank=True, null=True)
    team_2_quarter_2 = models.PositiveIntegerField(blank=True, null=True)
    team_2_quarter_3 = models.PositiveIntegerField(blank=True, null=True)
    team_2_quarter_4 = models.PositiveIntegerField(blank=True, null=True)
    team_2_win = models.PositiveIntegerField(blank=True, null=True)
    team_2_draw = models.PositiveIntegerField(blank=True, null=True)
    team_2_lose = models.PositiveIntegerField(blank=True, null=True)
    team_2_goal_score = models.IntegerField(blank=True, null=True)
    team_2_points = models.PositiveIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'match_result'


class Ranking(models.Model):
    team_no = models.PositiveIntegerField(primary_key=True)
    team_ranking = models.PositiveIntegerField()
    play_number = models.PositiveIntegerField()
    team_win = models.PositiveIntegerField()
    team_draw = models.PositiveIntegerField()
    team_lose = models.PositiveIntegerField()
    team_goal_score = models.IntegerField()
    team_points = models.PositiveIntegerField()

    class Meta:
        managed = False
        db_table = 'ranking'


class Report(models.Model):
    report_no = models.PositiveIntegerField(primary_key=True)
    team_no_1 = models.ForeignKey(FaTeam, models.DO_NOTHING, db_column='team_no_1')
    team_no_2 = models.ForeignKey(FaTeam, models.DO_NOTHING, db_column='team_no_2', related_name='report_team_no_2_set')
    stats_image_url = models.CharField(max_length=248, blank=True, null=True)
    share_image_url = models.CharField(max_length=248, blank=True, null=True)
    heatmap_image_url = models.CharField(max_length=248, blank=True, null=True)
    passmap_image_url = models.CharField(max_length=248, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'report'
