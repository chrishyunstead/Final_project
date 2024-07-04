import os
import subprocess
from main import tracking
from gen_viz import basic_gen
import cv2
import torch
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum, Count, Q, Case, When, IntegerField
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView, CreateView, UpdateView
from rest_framework import generics, permissions
from rest_framework.response import Response

from mysite import settings
from .forms import (
    TeamForm,
    MatchForm,
    MatchResultForm,
    MatchResultEditForm,
    DateSelectForm,
    TeamBoardForm,
    BoardCommentForm,
    MemberSelectForm,
)
from .models import Team, Match, MatchResult, Teamboard, BoardComment
from team.decorators import group_required

# from .serializers import MessageSerializer


# My Team 눌렀을때 반응
@login_required
def myteam(request, team_id=None):
    user = request.user

    # 팀을 선택하거나 특정 팀을 가져옵니다.
    if team_id:
        team = get_object_or_404(Team, team_no=team_id)
        if user not in team.members.all():
            return render(
                request,
                "team_create_form.html",
                {"message": "팀에 소속되어 있지 않습니다."},
            )
    else:
        if not user.teams.exists():
            return render(
                request,
                "team_create_form.html",
                {"message": "팀에 소속되어 있지 않습니다."},
            )
        team = user.teams.first()

    results = MatchResult.objects.filter(team=team)
    match_count = results.count()
    win_count = results.filter(result="W").count()
    draw_count = results.filter(result="D").count()
    lose_count = results.filter(result="L").count()
    goal_difference = sum(result.goal_difference for result in results)
    points = sum(result.points for result in results)

    # 모든 팀의 순위를 계산
    teams = Team.objects.all().order_by("-points", "-goal_difference")

    team_rankings = []
    for t in teams:
        team_rankings.append(
            {  # 순위
                "team": t,
                # 경기 수
                "match_count": t.match_count,
                "win_count": t.win_count,
                "draw_count": t.draw_count,
                "lose_count": t.lose_count,
                # 골득실
                "goal_difference": t.goal_difference,
                # 승점
                "points": t.points,
            }
        )

    # 모든 팀의 경기 일정 가져오기
    matches = Match.objects.all().order_by("-date")
    match_results = MatchResult.objects.all()

    context = {
        "team": team,
        "members": team.members.all(),
        "match_count": match_count,
        "win_count": win_count,
        "draw_count": draw_count,
        "lose_count": lose_count,
        "goal_difference": goal_difference,
        "points": points,
        "team_rankings": team_rankings,
        "matches": matches,
        "match_results": match_results,
    }
    return render(request, "team_dashboard.html", context)


# My Team 화면
# @login_required
# def team_dashboard(request, team_id):
#     team = get_object_or_404(Team, team_no=team_id)
#     user = request.user
#
#     if user not in team.members.all():
#         return render(
#             request,
#             "team_create_form.html",
#             {"message": "팀에 소속되어 있지 않습니다."},
#         )
#
#     # 팀의 경기 결과 및 순위 계산
#     results = MatchResult.objects.filter(team=team)
#     match_count = results.count()
#     win_count = results.filter(result="W").count()
#     draw_count = results.filter(result="D").count()
#     lose_count = results.filter(result="L").count()
#     goal_difference = sum(result.goal_difference for result in results)
#     points = sum(result.points for result in results)
#
#     context = {
#         "team": team,
#         "members": team.members.all(),
#         "match_count": match_count,
#         "win_count": win_count,
#         "draw_count": draw_count,
#         "lose_count": lose_count,
#         "goal_difference": goal_difference,
#         "points": points,
#     }
#
#     return render(request, "team_dashboard.html", context)


# 팀 생성하기화면
class CreateTeamView(LoginRequiredMixin, CreateView):
    model = Team
    form_class = TeamForm
    template_name = "crispy_form.html"
    extra_context = {"form_title": "팀 생성하기"}
    success_url = reverse_lazy("accounts:main")

    def dispatch(self, request, *args, **kwargs):
        if request.user.team_no or request.user.teams.exists():
            messages.warning(request, "이미 팀을 생성했거나 팀에 소속되어 있습니다.")
            return redirect("team:myteam")
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


# 팀프로필 업데이트
# updateview에서 알아서 pk인자 처리
class UpdateTeamView(LoginRequiredMixin, UpdateView):
    model = Team
    form_class = TeamForm
    template_name = "crispy_form.html"
    extra_context = {"form_title": "팀 프로필 수정하기"}
    success_url = reverse_lazy("team:myteam")

    def dispatch(self, request, *args, **kwargs):
        team = self.get_object()
        # 팀장만 수정가능
        if request.user != team.created_by:
            messages.warning(request, "팀 프로필을 수정할 권한이 없습니다.")
            return redirect("team:myteam")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, "팀 프로필이 성공적으로 수정되었습니다.")
        return super().form_valid(form)


update_team_profile = UpdateTeamView.as_view()


# 팀 가입할때 보여주는 팀 리스트
# 로그인한 사용자
@login_required
def team_list(request):
    teams = Team.objects.all()
    return render(request, "team_list.html", {"teams": teams})


# 팀 가입하기
# 로그인한 사용자
@login_required
def join_team(request, team_id):
    team = get_object_or_404(Team, team_no=team_id)
    user = request.user

    if user.teams.exists():
        messages.warning(request, "이미 다른 팀에 가입되어 있습니다.")
        return redirect("team:team_list")

    if not team.members.filter(pk=user.pk).exists():
        team.members.add(user)  # 팀에 사용자를 추가
        user.team_no = team  # 사용자의 team_no 필드 업데이트
        user.save()
        messages.success(request, f"{team.team_name} 팀에 가입되었습니다.")
    else:
        messages.warning(request, "이미 해당 팀에 가입되어 있습니다.")

    return redirect("team:team_list")


# 모든 경기 일정 보여줘서 Team Match 화면 보여줌
@login_required
def match_list(request):
    user = request.user
    if not user.team_no:
        return render(
            request,
            "team_create_form.html",
            {"message": "팀에 소속되어 있지 않습니다."},
        )

    matches = Match.objects.all()
    return render(request, "match_list.html", {"matches": matches, "user": user})


# 팀장인 사람만 경기 생성 가능
@login_required
def create_match(request):
    try:
        team = Team.objects.get(created_by=request.user)
    except Team.DoesNotExist:
        messages.error(request, "경기를 생성할 권한이 없습니다.")
        return redirect("team:match_list")

    if request.method == "POST":
        form = MatchForm(request.POST)
        if form.is_valid():
            match = form.save(commit=False)
            match.team = team
            match.save()
            return redirect("team:match_list")
    else:
        form = MatchForm()
    return render(request, "create_match.html", {"form": form})


# 경기 참여 버튼
# 팀이 있고 팀장인 사람만
@login_required
def join_match(request, match_id):
    match = get_object_or_404(Match, id=match_id)
    user = request.user
    team = user.team_no  # 사용자 팀을 가져옵니다.

    # 신청자가 팀장인지 확인
    if team is None or team.created_by != user:
        messages.error(request, "매칭 신청은 팀장만 가능합니다.")
        return redirect("team:match_list")

    # 같은 팀인지 확인
    if team == match.team:
        messages.error(request, "같은 팀에는 매칭 신청을 할 수 없습니다.")
        return redirect("team:match_list")

    # 매칭 신청
    if match.join_match(team):
        messages.success(
            request,
            "매칭 신청이 완료되었습니다. 상대팀 및 경기 일정에 대해서는 My Team의 경기 일정에서도 확인 가능합니다.",
        )
    else:
        messages.error(request, "이미 다른 팀이 매칭 신청을 완료했습니다.")
    return redirect("team:match_list")


# 팀스토리는 접근 제한은 로그인한 사용자만으로 지정
# @login_required
def team_story(request):
    user = request.user if request.user.is_authenticated else None
    team = user.team_no if user and user.team_no else None
    # results = (
    #     MatchResult.objects.filter(Q(team=team) | Q(opponent=team))
    #     if team
    #     else MatchResult.objects.none()
    # )

    # 모든 팀의 순위를 계산
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

    context = {
        "team": team,
        "team_rankings": team_rankings,
        "matches": matches,
    }
    return render(request, "team_story.html", context)


# 팀원 누구나라면 쓸수 있는 경기리포트 작성
# 팀에 속한 사람만


def update_team_ranking(team):
    team_results = team.results.all()
    match_count = team_results.count()
    win_count = team_results.filter(result="W").count()
    draw_count = team_results.filter(result="D").count()
    lose_count = team_results.filter(result="L").count()
    goal_difference = sum(result.goal_difference for result in team_results)
    points = sum(result.points for result in team_results)

    team.match_count = match_count
    team.win_count = win_count
    team.draw_count = draw_count
    team.lose_count = lose_count
    team.goal_difference = goal_difference
    team.points = points
    team.save()


@login_required
def create_match_result(request, team_id):
    team = get_object_or_404(Team, team_no=team_id)
    matches = Match.objects.filter(
        (Q(team=team) | Q(team_vs=team)) & Q(status="모집 마감")
    ).distinct()

    if request.method == "POST":
        form = MatchResultForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            match_result = form.save(commit=False)
            match_result.team = team
            match_result.created_by = request.user
            opponent_team = form.cleaned_data["opponent"]
            match_result.opponent = opponent_team

            # 상대 팀의 결과를 반영하여 MatchResult를 저장하고 양 팀의 랭킹을 업데이트
            if match_result.result == "W":
                opponent_result = "L"
            elif match_result.result == "D":
                opponent_result = "D"
            else:
                opponent_result = "W"

            opponent_match_result = MatchResult(
                team=opponent_team,
                opponent=team,
                date=match_result.date,
                result=opponent_result,
                goals_for=match_result.goals_against,
                goals_against=match_result.goals_for,
                created_by=request.user,
                video_file_left=match_result.video_file_left,
                video_file_right=match_result.video_file_right,
            )

            match_result.save()
            opponent_match_result.save()

            # 업데이트 팀 랭킹
            update_team_ranking(team)
            update_team_ranking(opponent_team)

            messages.success(request, "경기 결과가 성공적으로 저장되었습니다.")
            return redirect("team:myteam")
    else:
        form = MatchResultForm(user=request.user)

    return render(
        request,
        "create_match_result.html",
        {
            "form": form,
            "team": team,
            "matches": matches,
        },
    )


# 경기 결과 수정은 올린 사람만 가능하게끔
def edit_match_result(request, result_id):
    try:
        match_result = MatchResult.objects.get(pk=result_id, created_by=request.user)
    except MatchResult.DoesNotExist:
        messages.error(request, "해당 경기 리포트가 존재하지 않습니다.")
        return redirect("team:myteam")
    team = match_result.team
    opponent_team = match_result.opponent

    if request.method == "POST":
        if "delete" in request.POST:
            # 상대 팀의 결과 삭제
            opponent_match_result = MatchResult.objects.filter(
                team=opponent_team, opponent=team, date=match_result.date
            ).first()
            if opponent_match_result:
                opponent_match_result.delete()

            # 본인 팀의 결과 삭제
            match_result.delete()

            # 팀 랭킹 업데이트
            update_team_ranking(team)
            if opponent_team:
                update_team_ranking(opponent_team)

            messages.success(request, "경기 리포트가 성공적으로 삭제되었습니다.")
            return redirect("team:myteam")

        form = MatchResultEditForm(
            request.POST, request.FILES, instance=match_result, user=request.user
        )
        if form.is_valid():
            # form.save()
            match_result = form.save(commit=False)
            if "video_file_left" in request.FILES:
                match_result.video_file_left = request.FILES["video_file_left"]
            if "video_file_right" in request.FILES:
                match_result.video_file_right = request.FILES["video_file_right"]
            match_result.save()

            # 상대 팀의 결과 업데이트
            opponent_match_result = MatchResult.objects.filter(
                team=opponent_team, opponent=team, date=match_result.date
            ).first()
            if opponent_match_result:
                opponent_match_result.result = (
                    "W"
                    if match_result.result == "L"
                    else "L" if match_result.result == "W" else "D"
                )
                opponent_match_result.goals_for = match_result.goals_against
                opponent_match_result.goals_against = match_result.goals_for
                opponent_match_result.video_file_left = match_result.video_file_left
                opponent_match_result.video_file_right = match_result.video_file_right
                opponent_match_result.save()

            # 팀 랭킹 업데이트
            update_team_ranking(team)
            update_team_ranking(opponent_team)

            messages.success(request, "경기 결과가 성공적으로 수정되었습니다.")
            return redirect("team:myteam")
    else:
        form = MatchResultEditForm(instance=match_result, user=request.user)

    return render(
        request,
        "update_match_result.html",
        {
            "form": form,
            "match_result": match_result,
        },
    )


# @login_required
# def video_analysis(request, team_id):
#     team = get_object_or_404(Team, team_no=team_id)
#
#     if request.user not in team.members.all():
#         messages.error(request, "팀 구성원이 아닙니다.")
#         return redirect("team:myteam")
#
#     match_dates = (
#         MatchResult.objects.filter(Q(team=team) | Q(opponent=team))
#         .values_list("date", flat=True)
#         .distinct()
#     )
#
#     video_file_left = MatchResult.objects.filter(
#         Q(team=team) | Q(opponent=team)
#     ).values_list("video_file_left")
#     video_file_right = MatchResult.objects.filter(
#         Q(team=team) | Q(opponent=team)
#     ).values_list("video_file_right")
#
#     match_results = []
#     selected_date = None
#     if request.method == "POST":
#         form = DateSelectForm(request.POST, match_dates=match_dates)
#         member_form = MemberSelectForm(request.POST, team_members=team.members.all())
#         if form.is_valid():
#             selected_date = form.cleaned_data["date"]
#             match_results = MatchResult.objects.filter(
#                 Q(team=team) | Q(opponent=team), date=selected_date
#             ).exclude(video_file_left="", video_file_right="")
#
#         else:
#             member_form = None
#     else:
#         form = DateSelectForm(match_dates=match_dates)
#         # member_form = MemberSelectForm(team_members=team.members.all())
#         member_form = None
#         # match_results = MatchResult.objects.filter(
#         #     Q(team=team) | Q(opponent=team)
#         # ).exclude(
#         #     video_file=""
#         # )  # 초기에는 모든 날짜의 경기 결과 표시
#
#     return render(
#         request,
#         "video_analysis.html",
#         {
#             "team": team,
#             "match_results": match_results,
#             "form": form,
#             "member_form": member_form,
#             "selected_date": selected_date,
#             "video_file_left": video_file_left,
#             "video_file_right": video_file_right,
#         },
#     )


@login_required
def video_analysis(request, team_id):
    team = get_object_or_404(Team, team_no=team_id)

    if request.user not in team.members.all():
        messages.error(request, "팀 구성원이 아닙니다.")
        return redirect("team:myteam")

    match_dates = (
        MatchResult.objects.filter(Q(team=team) | Q(opponent=team))
        .values_list("date", flat=True)
        .distinct()
    )

    match_results = []
    selected_date = None
    viz_path_dict = {}

    if request.method == "POST":
        form = DateSelectForm(request.POST, match_dates=match_dates)
        # member_form = MemberSelectForm(request.POST, team_members=team.members.all())
        if form.is_valid():
            selected_date = form.cleaned_data["date"]
            match_results = MatchResult.objects.filter(
                Q(team=team) | Q(opponent=team), date=selected_date
            ).exclude(video_file_left="", video_file_right="")
            for match_result in match_results:
                left_video_path = match_result.video_file_left.path
                right_video_path = match_result.video_file_right.path
                stub_path = tracking(left_video_path, right_video_path)
                viz_path_dict = basic_gen(stub_path)
                # 저장된 이미지 파일 경로를 미디어 URL로 변환
                for key, value in viz_path_dict.items():
                    viz_path_dict[key] = os.path.join(settings.MEDIA_URL, value)
            else:
                form = DateSelectForm(match_dates=match_dates)
    else:
        form = DateSelectForm(match_dates=match_dates)

    return render(
        request,
        "video_analysis.html",
        {
            "team": team,
            "match_results": match_results,
            "form": form,
            "selected_date": selected_date,
            "viz_path_dict": viz_path_dict,
            # "member_form": member_form,
        },
    )


# @login_required
# def analyze_video(request, match_id):
#     match_result = get_object_or_404(MatchResult, pk=match_id)
#     team = match_result.team
#
#     if request.user not in team.members.all():
#         messages.error(request, "팀 구성원이 아닙니다.")
#         return redirect("team:myteam")
#
#     if request.method == "POST":
#         left_video_path = match_result.video_file_left.path
#         right_video_path = match_result.video_file_right.path
#
#         # 모델 분석 함수 호출
#         viz_path_dict = main(left_video_path, right_video_path)
#
#         return render(
#             request,
#             "result.html",
#             {
#                 "result_image_left": viz_path_dict["left_result"],
#                 "result_image_right": viz_path_dict["right_result"],
#             },
#         )
#
#     return redirect("team:video_analysis", team_id=team.team_no)


# def analysis_result_basic(request, team_id):
#     team = get_object_or_404(Team, team_no=team_id)
#     left_video_path = request["video_file_left"]
#     right_video_path = request["video_file_right"]
#     stub_path = main(left_video_path, right_video_path)
#     viz_path_dict = basic_gen(stub_path)
#     for key, value in viz_path_dict.items():
#         value = "adios_video/" + value
#     return viz_path_dict


# @login_required
# def analyze_video(request, match_id):
#     match_result = get_object_or_404(MatchResult, pk=match_id)
#     team = match_result.team
#
#     if request.user not in team.members.all():
#         messages.error(request, "팀 구성원이 아닙니다.")
#         return redirect("team:myteam")
#
#     if request.method == "POST":
#         video_path = match_result.video_file.path
#         output_path = os.path.join(settings.MEDIA_ROOT, "analysis", str(match_id))
#         os.makedirs(output_path, exist_ok=True)
#
#         # 모델 실행
#         command = f"python {os.path.join(settings.BASE_DIR, 'team', 'utils', 'main.py')} --video {video_path} --output {output_path}"
#         subprocess.run(command, shell=True)
#
#         # 분석 결과 이미지 경로
#         result_image_path = os.path.join(output_path, "result_image.png")
#
#         return render(
#             request,
#             "result.html",
#             {"result_image": result_image_path, "match_result": match_result},
#         )
#
#     return redirect("team:video_analysis", team_id=team.team_no)


def update_opponent_ranking(match_result):
    opponent_results = MatchResult.objects.filter(team=match_result.opponent)
    match_count = opponent_results.count()
    win_count = opponent_results.filter(result="W").count()
    draw_count = opponent_results.filter(result="D").count()
    lose_count = opponent_results.filter(result="L").count()
    goal_difference = sum(result.goal_difference for result in opponent_results)
    points = sum(result.points for result in opponent_results)

    opponent = match_result.opponent
    opponent.match_count = match_count
    opponent.win_count = win_count
    opponent.draw_count = draw_count
    opponent.lose_count = lose_count
    opponent.goal_difference = goal_difference
    opponent.points = points
    opponent.save()


# My Page 나의 팀 경기일정
# 팀에 속한 사람만 볼 수 있게
@login_required
def match_schedule(request):
    user = request.user
    team = user.team_no
    matches = Match.objects.filter(Q(team=team) | Q(team_vs=team))

    context = {
        "matches": matches,
    }
    return render(request, "match_schedule.html", context)


# My Page 팀 채팅
# 팀에 속한 사람만 볼 수 있게


# class MessageListCreateAPIView(generics.ListCreateAPIView):
#     serializer_class = MessageSerializer
#     permission_classes = [permissions.IsAuthenticated]
#
#     def get_queryset(self):
#         user_teams = self.request.user.teams.values_list("id", flat=True)
#         team_id = self.kwargs["team_id"]
#         if team_id in user_teams:
#             return Message.objects.filter(team_id=team_id).order_by("timestamp")
#         return Message.objects.none()
#
#     def perform_create(self, serializer):
#         team_id = self.kwargs["team_id"]
#         team = get_object_or_404(Team, pk=team_id)
#         if self.request.user in team.members.all():
#             serializer.save(user=self.request.user, team=team)
#         else:
#             return Response({"error": "User not in team"}, status=403)


# 할려고 했으나 잘 안됐음 웹소켓 문제 해결 못함
# def team_chat(request, team_id):
#     team = get_object_or_404(Team, pk=team_id)
#     if request.user in team.members.all():
#         return render(request, "team_chat.html", {"team": team})
#     return render(request, "access_denied.html")


# 팀원들 팀탈퇴기능
@login_required
def leave_team(request):
    user = request.user
    team = user.team_no
    if team:
        team.members.remove(user)
        user.team_no = None
        user.save()
        messages.success(request, "팀에서 탈퇴했습니다.")
    return redirect("accounts:main")


# 팀장 팀 삭제
@login_required
def delete_team(request):
    user = request.user
    team = user.team_no
    if team and team.created_by == user and team.members.count() == 1:
        team.delete()
        messages.success(request, "팀이 삭제되었습니다.")
    else:
        messages.error(
            request,
            "팀을 삭제할 수 없습니다. 팀에 다른 멤버가 존재하거나 권한이 없습니다.",
        )
    return redirect("accounts:main")


@login_required
def board_list(request, team_id):
    team = get_object_or_404(Team, pk=team_id)
    if request.user not in team.members.all():
        return redirect("team:team_dashboard", team_id=team_id)

    all_contents = Teamboard.objects.filter(team=team).order_by("-createDate")
    return render(
        request,
        "ourboard/board_list.html",
        {"all_contents": all_contents, "team": team},
    )


# view : 게시글 등록
@login_required
def board_create(request, team_id):
    team = get_object_or_404(Team, pk=team_id)
    if request.user not in team.members.all():
        return redirect("team:team_dashboard", team_id=team_id)

    if request.method == "GET":
        form = TeamBoardForm()
        return render(
            request, "ourboard/board_create.html", {"form": form, "team": team}
        )

    if request.method == "POST":
        form = TeamBoardForm(request.POST, request.FILES)
        if form.is_valid():
            board = form.save(commit=False)
            board.createUser = request.user
            board.team = team  # 게시글이 속한 팀 설정
            board.save()
            return redirect("team:board_list", team_id=team_id)
        else:
            context = {"form": form, "team": team}
            return render(request, "ourboard/board_create.html", context)


# view : 게시글 상세보기 + 댓글조회 + 댓글등록
def board_detail(request, team_id, pk):
    team = get_object_or_404(Team, pk=team_id)
    if request.user not in team.members.all():
        return redirect("team:team_dashboard", team_id=team_id)

    board = get_object_or_404(Teamboard, pk=pk, team=team)
    comment_board = BoardCommentForm()
    user_comment = board.comments.filter(commentUser=request.user).exists()

    if request.method == "POST":
        comment_form = BoardCommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.commentUser = request.user
            comment.teamboard = board
            comment.attendStatus = request.POST.get("attendStatus")
            comment.save()
            board.commentCnt += 1
            board.save()
            return redirect("team:board_detail", team_id=team_id, pk=board.pk)
    elif request.method == "GET":
        board.viewCnt += 1
        board.save()

    comments = board.comments.all()
    return render(
        request,
        "ourboard/board_detail.html",
        {
            "board": board,
            "comment_board": comment_board,
            "comments": comments,
            "user_comment": user_comment,
            "team": team,
        },
    )


# view : 게시글 수정
@login_required
def board_update(request, team_id, pk):
    team = get_object_or_404(Team, pk=team_id)
    if request.user not in team.members.all():
        return redirect("team:team_dashboard", team_id=team_id)

    board = get_object_or_404(Teamboard, pk=pk, team=team)
    if board.createUser != request.user:
        return redirect("team:board_list", team_id=team_id)

    if request.method == "POST":
        form = TeamBoardForm(request.POST, request.FILES, instance=board)
        if form.is_valid():
            update_board = form.save()
            return redirect("team:board_detail", team_id=team_id, pk=update_board.pk)
    else:
        form = TeamBoardForm(instance=board)
        context = {"form": form, "team": team, "pk": pk}
        return render(request, "ourboard/board_update.html", context)


# view : 게시글 삭제
@login_required
def board_delete(request, team_id, pk):
    team = get_object_or_404(Team, pk=team_id)
    if request.user not in team.members.all():
        return redirect("team:team_dashboard", team_id=team_id)

    board = get_object_or_404(Teamboard, pk=pk, team=team)
    if board.createUser != request.user:
        return redirect("team:board_list", team_id=team_id)

    if request.method == "POST":
        board.delete()
    return redirect("team:board_list", team_id=team_id)


# view : 게시글에 달린 댓글 삭제
@login_required
def board_comment_delete(request, team_id, pk):
    comment = get_object_or_404(BoardComment, pk=pk)
    teamboard_pk = comment.teamboard.pk  # 삭제 후 redirect할 때 사용할 teamboard의 pk
    team = comment.teamboard.team  # 댓글이 속한 팀을 가져옴

    # 현재 로그인한 사용자가 팀 멤버인지 확인
    if request.user not in team.members.all():
        return redirect("team:team_dashboard", team_id=team_id)

    # 현재 로그인한 사용자가 댓글을 작성한 사용자와 동일한지 확인
    if comment.commentUser != request.user:
        return redirect("team:board_list", team_id=team_id)

    if request.method == "POST":
        comment.delete()
        # 댓글이 삭제되었으므로 해당 게시글의 댓글 개수(commentCnt)를 1 감소시킴
        comment.teamboard.commentCnt -= 1
        comment.teamboard.save()
        return redirect("team:board_detail", team_id=team_id, pk=teamboard_pk)

    return render(
        request,
        "ourboard/board_comment_confirm_delete.html",
        {"comment": comment, "team": team},
    )


@login_required
def board_comment_update(request, team_id, pk):
    comment = get_object_or_404(BoardComment, pk=pk)
    team = comment.teamboard.team  # 댓글이 속한 팀을 가져옴

    # 현재 로그인한 사용자가 팀 멤버인지 확인
    if request.user not in team.members.all():
        return redirect("team:team_dashboard", team_id=team_id)

    # 현재 로그인한 사용자가 댓글을 작성한 사용자와 동일한지 확인
    if comment.commentUser != request.user:
        return redirect("team:board_list", team_id=team_id)

    if request.method == "POST":
        form = BoardCommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect(
                "team:board_detail", team_id=team_id, pk=comment.teamboard.pk
            )
    else:
        form = BoardCommentForm(instance=comment)

    return render(
        request,
        "ourboard/comment_update.html",
        {"form": form, "team": team, "comment": comment},
    )
