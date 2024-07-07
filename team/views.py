import os
import subprocess
from video_analysis.main import tracking
from video_analysis.gen_viz import basic_gen
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

    # 특정 팀 ID가 주어진 경우 해당 팀 조회
    if team_id:
        team = get_object_or_404(Team, team_no=team_id)
        # 사용자가 해당 팀에 소속되어있지 않은 경우 팀가입 및 생성 페이지로 이동시키고 메시지 송출
        if user not in team.members.all():
            return render(
                request,
                "team_create_form.html",
                {"message": "팀에 소속되어 있지 않습니다."},
            )
    # 사용자가 어떤 팀에도 속하지 않은 경우
    else:
        if not user.teams.exists():
            return render(
                request,
                "team_create_form.html",
                {"message": "팀에 소속되어 있지 않습니다."},
            )
        team = user.teams.first()

    # 팀의 경기 결과를 조회
    results = MatchResult.objects.filter(team=team)
    match_count = results.count()
    win_count = results.filter(result="W").count()
    draw_count = results.filter(result="D").count()
    lose_count = results.filter(result="L").count()
    goal_difference = sum(result.goal_difference for result in results)
    points = sum(result.points for result in results)

    # 모든 팀의 순위를 계산(승점, 골득실 기준으로 내림차순 정렬)
    teams = Team.objects.all().order_by("-points", "-goal_difference")

    # team_rankings 리스트에 담기
    team_rankings = []
    for t in teams:
        team_rankings.append(
            {  # 순위
                "team": t,
                # 경기 수
                "match_count": t.match_count,
                # 승
                "win_count": t.win_count,
                # 무
                "draw_count": t.draw_count,
                # 패
                "lose_count": t.lose_count,
                # 골득실
                "goal_difference": t.goal_difference,
                # 승점
                "points": t.points,
            }
        )

    # Match테이블에서 모든 팀의 경기 일정 가져오기(최신 날짜 순으로)
    matches = Match.objects.all().order_by("-date")

    # 모든 경기 결과를 조회
    match_results = MatchResult.objects.all()

    # team_dashboard.html에 전달할 데이터
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


# 팀 생성하기 화면
# 로그인 보장
class CreateTeamView(LoginRequiredMixin, CreateView):
    model = Team
    form_class = TeamForm
    template_name = "crispy_form.html"
    extra_context = {"form_title": "팀 생성하기"}
    success_url = reverse_lazy("accounts:main")

    def dispatch(self, request, *args, **kwargs):

        # 사용자가 이미 팀에 소속된 경우
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


# 팀 프로필 수정 페이지
# 로그인 보장
# updateview에서 알아서 pk인자 처리
class UpdateTeamView(LoginRequiredMixin, UpdateView):
    model = Team
    form_class = TeamForm
    template_name = "crispy_form.html"
    extra_context = {"form_title": "팀 프로필 수정하기"}
    success_url = reverse_lazy("team:myteam")

    def dispatch(self, request, *args, **kwargs):
        team = self.get_object()
        # 팀장만 수정 가능
        if request.user != team.created_by:
            messages.warning(request, "팀 프로필을 수정할 권한이 없습니다.")
            return redirect("team:myteam")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, "팀 프로필이 성공적으로 수정되었습니다.")
        return super().form_valid(form)


update_team_profile = UpdateTeamView.as_view()


# 팀 가입할때 보여주는 팀 목록 페이지
# 로그인한 사용자만 접근
@login_required
def team_list(request):
    # Team테이블 모든 객체 가져오기
    teams = Team.objects.all()
    return render(request, "team_list.html", {"teams": teams})


# 팀 가입 페이지
# 로그인한 사용자만 접근
@login_required
def join_team(request, team_id):
    team = get_object_or_404(Team, team_no=team_id)
    user = request.user

    if user.teams.exists():
        messages.warning(request, "이미 다른 팀에 가입되어 있습니다.")
        return redirect("team:team_list")

    if not team.members.filter(pk=user.pk).exists():
        team.members.add(user)  # 팀에 사용자를 추가(user의 pk로)
        user.team_no = team  # 사용자의 team_no 필드 업데이트
        user.save()
        messages.success(request, f"{team.team_name} 팀에 가입되었습니다.")
    else:
        messages.warning(request, "이미 해당 팀에 가입되어 있습니다.")

    return redirect("team:team_list")


# 경기 일정 목록 페이지(Team Match)
# 로그인한 사용자만 접근
@login_required
def match_list(request):
    user = request.user
    # user가 팀이 없으면 팀 생성화면으로 이동
    if not user.team_no:
        return render(
            request,
            "team_create_form.html",
            {"message": "팀에 소속되어 있지 않습니다."},
        )

    # 모든 Match 객체 불러오기
    matches = Match.objects.all()
    return render(request, "match_list.html", {"matches": matches, "user": user})


# 경기 생성 페이지
# 로그인한 사용자만 접근
# 팀의 생성자인 팀장만 경기 생성 가능
@login_required
def create_match(request):
    # 팀장인 사람만
    try:
        team = Team.objects.get(created_by=request.user)
    # 팀이 없는 사람들은 Team Match화면으로 이동
    except Team.DoesNotExist:
        messages.error(request, "경기를 생성할 권한이 없습니다.")
        return redirect("team:match_list")

    # 경기 생성
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


# 경기 참여 페이지
# 로그인한 사용자만 접근
# 팀이 있고 팀장인 사용자만 경기 참여 가능
@login_required
def join_match(request, match_id):
    match = get_object_or_404(Match, id=match_id)
    user = request.user
    team = user.team_no  # 사용자 팀을 가져옵니다.

    # 신청자가 팀장인지 확인
    if team is None or team.created_by != user:
        messages.error(request, "매칭 신청은 팀장만 가능합니다.")
        return redirect("team:match_list")

    # 본인이 만든 매치를 본인이 신청할 수 없음
    if team == match.team:
        messages.error(request, "같은 팀에는 매칭 신청을 할 수 없습니다.")
        return redirect("team:match_list")

    # 매칭 신청
    if match.join_match(team):
        messages.success(
            request,
            "매칭 신청이 완료되었습니다. 상대팀 및 경기 일정에 대해서는 My Team의 경기 일정에서도 확인 가능합니다.",
        )
    # 매칭이 이미 마감되었을때
    else:
        messages.error(request, "이미 다른 팀이 매칭 신청을 완료했습니다.")
    return redirect("team:match_list")


# Team Story 페이지
# 팀스토리는 접근 제한이 없음
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
    # 모든 팀의 경기 결과 가져오기
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


# 팀 순위 업데이트 함수
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


# 경기 리포트 자성 생성 페이지
# 로그인한 사용자만
# 팀에 속한 사용자만
@login_required
def create_match_result(request, team_id):
    team = get_object_or_404(Team, team_no=team_id)

    # 사용자팀하고, 상대팀 매치중 모집마감 상태인 매치만 보여주기
    matches = Match.objects.filter(
        (Q(team=team) | Q(team_vs=team)) & Q(status="모집 마감")
    ).distinct()

    if request.method == "POST":
        # 경기 결과, 비디오 파일도 받을거임
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


# 경기 결과 수정은 경기 리포트 작성한 사람만 가능하게끔
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


# 영상분석 페이지
# 로그인한 사용자만
# 같은 팀의 멤버들만 이용가능
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

            # 왼쪽 경기 영상, 오른쪽 경기 영상 나눠서 받고 경기 영상 분석 모델에 경로 전달
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
        },
    )


# 상대팀 순위 업데이트 함수
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


# My Page의 나의 팀 경기일정
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


# 로그인한 사용자만
# 해당팀에 속한 사용자만
# 팀원들 팀탈퇴 기능
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


# 로그인한 사용자만
# 해당팀에 속한 사용자만
# 팀장 팀 삭제기능
@login_required
def delete_team(request):
    user = request.user
    team = user.team_no
    # 팀 삭제는 팀에 팀원이 없을시에만 가능하게끔
    if team and team.created_by == user and team.members.count() == 1:
        team.delete()
        messages.success(request, "팀이 삭제되었습니다.")
    else:
        messages.error(
            request,
            "팀을 삭제할 수 없습니다. 팀에 다른 멤버가 존재하거나 권한이 없습니다.",
        )
    return redirect("accounts:main")


# 로그인한 사용자만
# 해당팀에 속한 사용자만
# 게시글 목록 페이지
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


# 로그인한 사용자만
# 해당팀에 속한 사용자만
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


# 로그인한 사용자만
# 해당팀에 속한 사용자만
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


# 로그인한 사용자만
# 해당팀에 속한 사용자만
# 게시글 수정
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


# 로그인한 사용자만
# 해당팀에 속한 사용자만
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


# 로그인한 사용자만
# 해당팀에 속한 사용자만
# 게시글에 달린 댓글 삭제
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


# 로그인한 사용자만
# 해당팀에 속한 사용자만
# 게시글에 달린 댓글 수정
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
