from typing import Optional

from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Q
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView as DjangoLoginView, RedirectURLMixin
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.views import View
from django.views.decorators.csrf import csrf_protect
from django.views.generic import CreateView, UpdateView, DetailView

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

from mysite import settings

#
# class SignupView(RedirectURLMixin, CreateView):
#     model = Authentication
#     form_class = SignupForm
#     template_name = "accounts/signup.html"
#     extra_context = {
#         "form_title": "회원가입",
#     }
#     success_url = reverse_lazy("accounts:profile")
#
#     def dispatch(self, request, *args, **kwargs):
#         if self.request.user.is_authenticated:
#             redirect_to = self.success_url
#             if redirect_to != request.path:
#                 messages.warning(request, "로그인 유저는 회원가입할 수 없습니다.")
#                 return HttpResponseRedirect(redirect_to)
#         return super().dispatch(request, *args, **kwargs)
#
#     def form_valid(self, form):
#         user = form.cleaned_data.get("user_no")
#         auth_user = Authentication.objects.create(
#             user_no=user,
#             user=form.cleaned_data.get("user"),
#             username=form.cleaned_data.get("username"),
#             cell_phone=form.cleaned_data.get("cell_phone"),
#             email=form.cleaned_data.get("email"),
#             birthday=form.cleaned_data.get("birthday"),
#             gender=form.cleaned_data.get("gender"),
#         )
#         auth_user.set_password(form.cleaned_data.get("password1"))
#         auth_user.save()
#
#         profile = Profile.objects.create(
#             user_no=user,
#             position_1=form.cleaned_data.get("position_1"),
#             ability_1=form.cleaned_data.get("ability_1"),
#             level=form.cleaned_data.get("level"),
#             sigg_no=form.cleaned_data.get("sigg_name"),
#         )
#         profile.save()
#
#         messages.success(self.request, "회원가입을 환영합니다. ;-)")
#         auth_login(self.request, auth_user)
#         return super().form_valid(form)
#
#
# signup = SignupView.as_view()


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

#
# class SignupView(View):
#     def get(self, request):
#         sido_names = SiggAreas.objects.values_list("sido_name", flat=True).distinct()
#         return render(request, "accounts/signup.html", {"sido_names": sido_names})
#
#     def post(self, request):
#         form = SignupForm(request.POST)
#         if form.is_valid():
#             user = form.save()
#             login(request, user)
#             return redirect("accounts:profile")
#         return render(request, "accounts/signup.html", {"form": form})
#         user_id = request.POST["user_id"]
#         username = request.POST["username"]
#         email = request.POST["email"]
#         birth_date = request.POST["birth_date"]
#         gender = request.POST["gender"]
#         cellphone = request.POST["cellphone"]
#         sido_name = request.POST["sido_name"]
#         sigg_name = request.POST["sigg_name"]
#         position_1 = request.POST["position_1"]
#         ability_1 = request.POST["ability_1"]
#         level = request.POST["level"]
#         password = make_password(request.POST["password"])
#
#         user = User.objects.create(
#             user_id=user_id,
#             username=username,
#             email=email,
#             birth_date=birth_date,
#             gender=gender,
#             cellphone=cellphone,
#             sido_name_id=sido_name,
#             sigg_name_id=sigg_name,
#             position_1=position_1,
#             ability_1=ability_1,
#             level=level,
#             password=password,
#         )
#         auth_login(request, user)
#         return redirect("accounts:profile")


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


# 메인화면 뷰
@login_required
def main(request):
    return render(request, "base.html")


# 마이페이지 뷰
# @login_required
# def mypage_view(request):
#     return render(request, "accounts/mypage.html", {"user": request.user})


# @login_required
# def edit_mypage(request):
#     # 입력받은 폼 필드값들 받아서 인스탄스 변수에 저장
#     if request.method == "POST":
#         form = EditProfileForm(request.POST, request.FILES, instance=request.user)
#         if form.is_valid():
#             form.save()
#             return redirect("accounts:mypage")
#     # 마이페이지 방문시 GET요청으로 사용자 정보 불러옴
#     else:
#         form = EditProfileForm(instance=request.user)
#     return render(request, "accounts/edit_mypage.html", {"form": form})


@method_decorator(login_required, name="dispatch")
class MyPageView(DetailView):
    model = User
    template_name = "accounts/mypage.html"
    context_object_name = "user"

    def get_object(self):
        return self.request.user


mypage_view = MyPageView.as_view()


# @method_decorator(login_required, name="dispatch")
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
        form = CustomPasswordChangeForm(request.user)
    return render(request, "accounts/password_change.html", {"form": form})


@login_required
def password_change_done(request):
    return render(request, "accounts/password_change_done.html")


from django.contrib.auth.views import PasswordResetView as DjangoPasswordResetView
from django.contrib.auth.views import (
    PasswordResetConfirmView as DjangoPasswordResetConfirmView,
)


class PasswordResetView(DjangoPasswordResetView):
    email_template_name = "accounts/password_reset_email.html"
    success_url = reverse_lazy("accounts:password_reset")

    def form_valid(self, form) -> HttpResponse:
        response = super().form_valid(form)
        messages.success(
            self.request,
            (
                "비밀번호 재설정 메일을 발송했습니다. 계정이 존재한다면 입력하신 이메일로 "
                "비밀번호 재설정 안내문을 확인하실 수 있습니다. "
                "만약 이메일을 받지 못했다면 등록하신 이메일을 다시 확인하시거나 스팸함을 확인해주세요."
            ),
        )
        return response


password_reset = PasswordResetView.as_view()


class PasswordResetConfirmView(DjangoPasswordResetConfirmView):
    post_reset_login = True
    # 암호 재설정 후 로그인페이지로 이동시키기
    success_url = settings.LOGIN_REDIRECT_URL

    def form_valid(self, form) -> HttpResponse:
        response = super().form_valid(form)

        messages.success(self.request, "암호를 재설정하고, 자동 로그인했습니다.")

        return response


password_reset_confirm = PasswordResetConfirmView.as_view()


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
