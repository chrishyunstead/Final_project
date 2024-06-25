from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path("signup/", views.signup, name="signup"),
    # path("get-districts/", GetDistrictsView.as_view(), name="get-districts"),
    path("login/", views.login, name="login"),
    path("logout/", views.logout, name="logout"),
    # 회원탈퇴
    path("delete_user/", views.delete_user, name="delete_user"),
    # 메인화면
    path("", views.main, name="main"),
    path("mypage/", views.mypage_view, name="mypage"),
    path("edit_mypage", views.edit_mypage, name="edit_mypage"),
    path("password_change/", views.password_change, name="password_change"),
    path(
        "password_change/done/", views.password_change_done, name="password_change_done"
    ),
    path("find_id/", views.find_id, name="find_id"),
    path("password_reset/", views.password_reset, name="password_reset"),
    path(
        "password_reset/done/",
        views.PasswordResetDoneView.as_view(
            template_name="accounts/password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        views.password_reset_confirm,
        name="password_reset_confirm",
    ),
]
