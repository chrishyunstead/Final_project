from django.urls import path
from . import views

app_name = "team"
urlpatterns = [
    # 마이팀 누르면 팀생성하기 또는 팀 가입하기 보여주기
    path("myteam/", views.myteam, name="myteam"),
    # 팀 생성하기
    path("create_team/", views.create_team, name="create_team"),
    # 팀 가입하기 누르면 팀들 나오고 가입하기까지
    path("team_list/", views.team_list, name="team_list"),
    # 마이 팀페이지
    path("team_dashboard/", views.team_dashboard, name="team_dashboard"),
    path("join_team/<int:team_id>/", views.join_team, name="join_team"),
]
