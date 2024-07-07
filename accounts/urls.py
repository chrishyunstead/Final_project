from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    # 회원가입
    path("signup/", views.signup, name="signup"),
    # 로그인
    path("login/", views.login, name="login"),
    # 로그아웃
    path("logout/", views.logout, name="logout"),
    # 회원탈퇴
    path("delete_user/", views.delete_user, name="delete_user"),
    # 메인화면
    path("", views.main, name="main"),
    # 마이페이지
    path("mypage/", views.mypage_view, name="mypage"),
    # 마이페이지 수정
    path("edit_mypage", views.edit_mypage, name="edit_mypage"),
    # 비밀번호 변경
    path("password_change/", views.password_change, name="password_change"),
    # 비밀번호 변경 완료 화면
    path(
        "password_change/done/", views.password_change_done, name="password_change_done"
    ),
    # 아이디 찾기
    path("find_id/", views.find_id, name="find_id"),
    # 비밀번호 찾기(초기화)
    path("password_reset/", views.password_reset, name="password_reset"),
    # 비밀번호 초기화 메일 발송 완료 화면
    path(
        "password_reset/done/",
        views.PasswordResetDoneView.as_view(
            template_name="accounts/password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    # 새 비밀번호 설정 완료
    path(
        "reset/<uidb64>/<token>/",
        views.password_reset_confirm,
        name="password_reset_confirm",
    ),
]
