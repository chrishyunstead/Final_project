from typing import Optional

import feedparser
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Q
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView as DjangoLoginView, RedirectURLMixin
from django.template import loader
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.views import View
from django.views.decorators.csrf import csrf_protect
from django.views.generic import CreateView, UpdateView, DetailView
from django.contrib.auth.views import PasswordResetView as DjangoPasswordResetView
from django.contrib.auth.views import (
    PasswordResetConfirmView as DjangoPasswordResetConfirmView,
)

import team
from accounts.forms import (
    LoginForm,
    SignupForm,
    CustomPasswordChangeForm,
    PasswordResetForm,
    UsernameRecoveryForm,
    EditProfileForm,
)
from django.contrib.auth.views import LogoutView as DjangoLogoutView

from django.contrib import messages
from django.contrib.auth import (
    login as auth_login,
    update_session_auth_hash,
    get_user_model,
)
from accounts.models import User, Profile, SiggAreas
from accounts.utils import send_welcome_email
from django.contrib.auth.views import PasswordChangeView as DjangoPasswordChangeView
from django.contrib.auth.tokens import default_token_generator as token_generator

from mysite import settings
from django.contrib.auth.views import (
    PasswordResetDoneView as DjangoPasswordResetDoneView,
    PasswordResetCompleteView as DjangoPasswordResetCompleteView,
)

from team.models import Team, Match, MatchResult


# 회원가입, 크리스피html이용
class SignupView(RedirectURLMixin, CreateView):
    model = User
    form_class = SignupForm
    template_name = "crispy_form.html"
    extra_context = {
        "form_title": "회원가입",
    }
    success_url = reverse_lazy("accounts:main")

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            redirect_to = self.success_url
            if redirect_to != request.path:
                messages.warning(request, "로그인 유저는 회원가입할 수 없습니다.")
                return HttpResponseRedirect(redirect_to)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "회원가입을 환영합니다. ;-)")

        user = self.object
        auth_login(self.request, user)

        messages.success(self.request, "회원가입과 동시에 로그인 지원 !")
        send_welcome_email(user, fail_silently=True)
        return response


signup = SignupView.as_view()


class LoginView(DjangoLoginView):

    # 로그인 유저 회원가입 및 로그인 시도 막기
    redirect_authenticated_user = True

    form_class = LoginForm
    template_name = "crispy_form.html"

    extra_context = {
        "form_title": "로그인",
    }
    success_url = reverse_lazy("accounts:main")


login = LoginView.as_view()


class LogoutView(DjangoLogoutView):
    next_page = "accounts:login"

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        messages.success(request, "로그아웃했습니다. :-)")
        return response


logout = LogoutView.as_view()


# 메인 페이지에 축구 기사 가져오기 함수
def fetch_football_news():
    feed_url = "https://feeds.bbci.co.uk/sport/rss.xml?edition=uk"  # BBC Sport 예시
    news_feed = feedparser.parse(feed_url)
    articles = []
    for entry in news_feed.entries[:5]:  # 최근 5개의 기사를 가져옵니다.
        articles.append(
            {
                "title": entry.title,
                "link": entry.link,
                "published": entry.published,
            }
        )
    return articles


# 회원탈퇴
@login_required
def delete_user(request):
    user = request.user
    if user.team_no:
        messages.error(request, "팀 탈퇴를 먼저 진행해야 회원 탈퇴가 가능합니다.")
        return redirect("accounts:mypage")
    if request.method == "POST":
        user.delete()
        messages.success(request, "회원탈퇴가 완료되었습니다.")
        logout(request)
        return redirect("accounts:main")
    return render(request, "accounts/delete_user.html")


# 메인화면 뷰
def main(request):
    user = request.user if request.user.is_authenticated else None
    team = user.team_no if user and user.team_no else None
    # results = MatchResult.objects.filter(team=team) if team else None
    teams = Team.objects.all().order_by("-points", "-goal_difference")
    team_rankings = []
    for t in teams:
        team_rankings.append(
            {
                "team": t,
                "match_count": t.match_count,
                "win_count": t.win_count,
                "draw_count": t.draw_count,
                "lose_count": t.lose_count,
                "goal_difference": t.goal_difference,
                "points": t.points,
            }
        )

    # 모든 팀의 경기 일정 가져오기
    matches = Match.objects.all().order_by("-date")
    match_results = MatchResult.objects.all()

    # 경기 일정에 결과 추가
    match_results_dict = {}
    for result in match_results:
        match_key = (result.date, result.team_id, result.opponent_id)
        match_results_dict[match_key] = result

    for match in matches:
        match_key_1 = (match.date, match.team_id, match.team_vs_id)
        match_key_2 = (match.date, match.team_vs_id, match.team_id)
        match.result = match_results_dict.get(match_key_1) or match_results_dict.get(
            match_key_2
        )

    # 축구 뉴스 기사 가져오기
    articles = fetch_football_news()

    context = {
        "team": team,
        "team_rankings": team_rankings,
        "matches": matches,
        "articles": articles,
    }
    return render(request, "accounts/main.html", context)


@method_decorator(login_required, name="dispatch")
class MyPageView(DetailView):
    model = User
    template_name = "accounts/mypage.html"

    context_object_name = "user"

    def get_object(self):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["team"] = self.request.user.team_no
        return context


mypage_view = MyPageView.as_view()


class EditProfileView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = EditProfileForm
    template_name = "crispy_form.html"
    extra_context = {
        "form_title": "프로필 수정",
    }
    success_url = reverse_lazy("accounts:mypage")

    def get_object(self, queryset=None) -> Optional[User]:
        if not self.request.user.is_authenticated:
            return None

        try:
            return self.request.user
        except User.DoesNotExist:
            return None

    def form_valid(self, form):
        profile = form.save(commit=False)
        profile.user = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, "프로필을 저장했습니다.")
        return response


edit_mypage = EditProfileView.as_view()


@login_required
def password_change(request):
    if request.method == "POST":
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "비밀번호가 성공적으로 변경되었습니다.")
            return render(request, "accounts/password_change_done.html")
        else:
            for error in form.errors.values():
                messages.error(request, error)
    else:
        form = CustomPasswordChangeForm(request.user)
    return render(request, "accounts/password_change.html", {"form": form})


@login_required
def password_change_done(request):
    return render(request, "accounts/password_change_done.html")


class PasswordResetView(DjangoPasswordResetView):
    template_name = "accounts/password_reset_form.html"
    email_template_name = "accounts/password_reset_email.html"
    success_url = reverse_lazy("accounts:main")
    form_class = PasswordResetForm

    def form_valid(self, form):
        email = form.cleaned_data.get("email")
        users = User.objects.filter(email=email, is_active=True)

        for user in users:
            token = token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            context = {
                "email": email,
                "domain": self.request.get_host(),
                "site_name": "Your Site Name",
                "uid": uid,
                "user": user,  # Add user to context
                "token": token,
                "protocol": "https" if self.request.is_secure() else "http",
            }
            subject = "Password Reset on Your Site Name"
            email_template_name = self.email_template_name
            email_content = loader.render_to_string(email_template_name, context)
            send_mail(subject, email_content, settings.DEFAULT_FROM_EMAIL, [user.email])

        messages.success(
            self.request,
            (
                "비밀번호 재설정 메일을 발송했습니다. 계정이 존재한다면 입력하신 이메일로 "
                "비밀번호 재설정 안내문을 확인하실 수 있습니다. "
                "만약 이메일을 받지 못했다면 등록하신 이메일을 다시 확인하시거나 스팸함을 확인해주세요."
            ),
        )
        return HttpResponseRedirect(self.success_url)


password_reset = PasswordResetView.as_view()


class PasswordResetConfirmView(DjangoPasswordResetConfirmView):
    template_name = "accounts/password_reset_confirm.html"
    post_reset_login = True
    success_url = reverse_lazy("accounts:main")

    def form_valid(self, form) -> HttpResponse:
        response = super().form_valid(form)
        messages.success(self.request, "암호를 재설정하고, 자동 로그인했습니다.")
        return response


password_reset_confirm = PasswordResetConfirmView.as_view()


class PasswordResetDoneView(DjangoPasswordResetDoneView):
    template_name = "accounts/password_reset_done.html"


password_reset_done = PasswordResetDoneView.as_view()


def find_id(request):
    if request.method == "POST":
        form = UsernameRecoveryForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            email = form.cleaned_data["email"]
            try:
                user = User.objects.get(username=username, email=email)
                messages.success(request, f"아이디: {user.user_id}")
            except User.DoesNotExist:
                messages.error(request, "입력하신 정보와 일치하는 사용자가 없습니다.")
    else:
        form = UsernameRecoveryForm()

    return render(request, "accounts/find_user_id.html", {"form": form})
