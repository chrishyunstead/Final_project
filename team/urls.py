from django.urls import path
from . import views

# from .views import MessageListCreateAPIView

app_name = "team"
urlpatterns = [
    # 마이팀 누르면 팀생성하기 또는 팀 가입하기 보여주기
    path("myteam/", views.myteam, name="myteam"),
    path("myteam/<int:team_id>/", views.myteam, name="team_dashboard"),
    # 팀 생성하기
    path("create_team/", views.create_team, name="create_team"),
    # 팀프로필 수정
    path(
        "update_team_profile/<int:pk>/",
        views.update_team_profile,
        name="update_team_profile",
    ),
    # 팀 가입하기 누르면 팀들 나오고 가입하기까지
    path("team_list/", views.team_list, name="team_list"),
    # 마이 팀페이지
    # path("team_dashboard/<int:team_id>/", views.team_dashboard, name="team_dashboard"),
    path("join_team/<int:team_id>/", views.join_team, name="join_team"),
    path("matches/", views.match_list, name="match_list"),
    path("matches/create/", views.create_match, name="create_match"),
    path("matches/join/<int:match_id>/", views.join_match, name="join_match"),
    path(
        "match_report/<int:team_id>/",
        views.create_match_result,
        name="match_report",
    ),
    path(
        "match_report_edit/<int:result_id>/",
        views.edit_match_result,
        name="match_report_edit",
    ),
    path("match_schedule/", views.match_schedule, name="match_schedule"),
    path("team_story/", views.team_story, name="team_story"),
    # path("chat/<int:team_id>/", views.team_chat, name="team_chat"),
    # path(
    #     "api/messages/<int:team_id>/",
    #     MessageListCreateAPIView.as_view(),
    #     name="message-list-create",
    # ),
    path("video_analysis/<int:team_id>/", views.video_analysis, name="video_analysis"),
    # 영상분석 시작 버튼
    # path(
    #     "analyze_video/<int:match_id>/",
    #     views.analyze_video,
    #     name="analyze_video",
    # ),
    path("leave_team/", views.leave_team, name="leave_team"),
    path("delete_team/", views.delete_team, name="delete_team"),
    # 게시판 리스트 url
    path("board/<int:team_id>/", views.board_list, name="board_list"),
    path("board/<int:team_id>/create/", views.board_create, name="board_create"),
    path("board/<int:team_id>/<int:pk>/", views.board_detail, name="board_detail"),
    path(
        "board/<int:team_id>/<int:pk>/update/", views.board_update, name="board_update"
    ),
    path(
        "board/<int:team_id>/<int:pk>/delete/", views.board_delete, name="board_delete"
    ),
    path(
        "board/<int:team_id>/<int:pk>/comment_delete/",
        views.board_comment_delete,
        name="board_comment_delete",
    ),
    path(
        "board/<int:team_id>/<int:pk>/comment_update/",
        views.board_comment_update,
        name="board_comment_update",
    ),
    # path(
    #     "video_analysis/<int:team_id>/result/",
    #     views.analysis_result_basic,
    #     name="analysis_result_basic",
    # ),
]
