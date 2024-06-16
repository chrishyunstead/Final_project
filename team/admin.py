from django.contrib import admin
from .models import Team


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ("team_name", "get_members_usernames", "create_date", "created_by")
    search_fields = ("team_name", "members__username", "created_by__username")

    def get_members_usernames(self, obj):
        return obj.get_members_usernames()

    get_members_usernames.short_description = "Members"
