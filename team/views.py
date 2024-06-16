from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView, CreateView

from .forms import TeamForm
from .models import Team
from team.decorators import group_required


@login_required
def myteam(request):
    user = request.user
    if not user.team_no:
        return render(
            request,
            "team_create_form.html",
            {"message": "팀에 소속되어 있지 않습니다."},
        )
    return redirect("team:team_dashboard")  # 팀 대시보드 페이지로 리디렉션


@login_required
def team_dashboard(request):
    user = request.user
    team = user.team_no

    context = {
        "team": team,
        "members": team.members.all(),
    }

    if not team:
        return redirect("team:create_team")

    return render(request, "team_dashboard.html", context)


class CreateTeamView(LoginRequiredMixin, CreateView):
    model = Team
    form_class = TeamForm
    template_name = "crispy_form.html"
    extra_context = {"form_title": "팀 생성하기"}
    success_url = reverse_lazy("core:base")

    def dispatch(self, request, *args, **kwargs):
        if request.user.team_no:
            messages.warning(request, "이미 팀을 생성했거나 팀에 소속되어 있습니다.")
            return redirect("team:team_dashboard")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        team = form.save(commit=False)
        team.created_by = self.request.user
        team.save()
        self.request.user.team_no = team
        self.request.user.save()
        messages.success(self.request, "팀이 성공적으로 생성되었습니다.")
        return super().form_valid(form)


create_team = CreateTeamView.as_view()


@login_required
def team_list(request):
    teams = Team.objects.all()
    return render(request, "team_list.html", {"teams": teams})


@login_required
def join_team(request, team_id):
    team = get_object_or_404(Team, team_no=team_id)
    user = request.user

    if not team.members.filter(pk=user.pk).exists():
        team.members.add(user)  # 팀에 사용자를 추가
        user.team_no = team  # 사용자의 team_no 필드 업데이트
        user.save()
        messages.success(request, f"{team.team_name} 팀에 가입되었습니다.")
    else:
        messages.warning(request, "이미 해당 팀에 가입되어 있습니다.")

    return redirect("team:team_list")
