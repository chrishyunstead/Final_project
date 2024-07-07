from django.conf import settings
from django.db import models
from django.contrib.auth.models import Group


class Court(models.Model):
    # 경기장 정보
    court_no = models.PositiveSmallIntegerField(primary_key=True)
    court_name = models.CharField(max_length=50)
    court_address = models.CharField(max_length=100)
    sido_name = models.CharField(max_length=10)
    sigg_name = models.CharField(max_length=10)
    number_3vs3 = models.TextField(
        db_column="3vs3"
    )  # Field renamed because it wasn't a valid Python identifier. This field type is a guess.
    number_4vs4 = models.TextField(
        db_column="4vs4"
    )  # Field renamed because it wasn't a valid Python identifier. This field type is a guess.
    number_5vs5 = models.TextField(
        db_column="5vs5"
    )  # Field renamed because it wasn't a valid Python identifier. This field type is a guess.
    number_6vs6 = models.TextField(
        db_column="6vs6"
    )  # Field renamed because it wasn't a valid Python identifier. This field type is a guess.
    number_7vs7 = models.TextField(
        db_column="7vs7"
    )  # Field renamed because it wasn't a valid Python identifier. This field type is a guess.
    number_8vs8 = models.TextField(
        db_column="8vs8"
    )  # Field renamed because it wasn't a valid Python identifier. This field type is a guess.
    number_9vs9 = models.TextField(
        db_column="9vs9"
    )  # Field renamed because it wasn't a valid Python identifier. This field type is a guess.
    number_11vs11 = models.TextField(
        db_column="11vs11"
    )  # Field renamed because it wasn't a valid Python identifier. This field type is a guess.

    # 기타 시설 정보
    cool_heating = models.TextField()  # This field type is a guess.
    cooling = models.TextField()  # This field type is a guess.
    team_vest = models.TextField()  # This field type is a guess.
    training_zone = models.TextField()  # This field type is a guess.
    rent_balls = models.TextField()  # This field type is a guess.
    rent_shoes = models.TextField()  # This field type is a guess.
    shower_room = models.TextField()  # This field type is a guess.
    parking = models.TextField()  # This field type is a guess.

    class Meta:
        managed = False
        db_table = "court"


class Team(models.Model):
    team_no = models.AutoField(primary_key=True)
    team_name = models.CharField(unique=True, max_length=10)
    team_image_url = models.ImageField(blank=True, null=True)
    team_day = models.CharField(max_length=15)
    team_timeslot = models.CharField(max_length=10)
    team_ages = models.CharField(max_length=10)

    # 팀 성별 선택
    GENDER_CHOICES = [
        ("여성", "여성"),
        ("남성", "남성"),
        ("혼성", "혼성"),
    ]
    gender = models.CharField(
        max_length=2, choices=GENDER_CHOICES, null=True, blank=True
    )
    team_level = models.IntegerField(null=True, blank=True)
    create_date = models.DateTimeField(auto_now_add=True)

    # 팀 멤버
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="teams", blank=True
    )
    # 팀장 지정
    created_by = models.OneToOneField(
        settings.AUTH_USER_MODEL, related_name="created_team", on_delete=models.CASCADE
    )
    sido_name = models.CharField(max_length=10)
    sigg_name = models.CharField(max_length=10)
    court_name = models.CharField(max_length=50)

    # 경기 기록
    match_count = models.PositiveIntegerField(default=0)
    win_count = models.PositiveIntegerField(default=0)
    draw_count = models.PositiveIntegerField(default=0)
    lose_count = models.PositiveIntegerField(default=0)
    goal_difference = models.IntegerField(default=0)
    points = models.PositiveIntegerField(default=0)

    class Meta:
        managed = True
        db_table = "team"

    def __str__(self):
        return self.team_name

    def get_members_usernames(self):
        return ", ".join([member.username for member in self.members.all()])

    def is_leader(self, user):
        return self.created_by == user

    def delete(self, *args, **kwargs):
        # 팀 삭제 시 members 필드를 비워야 합니다.
        self.members.clear()
        super().delete(*args, **kwargs)


# 팀 채팅 메시지
# class Message(models.Model):
#     team = models.ForeignKey(
#         "team.Team", related_name="messages", on_delete=models.CASCADE
#     )
#     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#     content = models.TextField()
#     timestamp = models.DateTimeField(auto_now_add=True)
#
#     def __str__(self):
#         return f"{self.user.username}: {self.content[:20]}"


# 팀 매치
class Match(models.Model):
    team = models.ForeignKey(
        "team.Team",
        on_delete=models.SET_NULL,
        null=True,
        related_name="matches",
    )
    team_vs = models.ForeignKey(
        "team.Team",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="applied_matches",
    )
    date = models.DateField()
    time = models.TimeField()
    sido_name = models.CharField(max_length=10)
    sigg_name = models.CharField(max_length=10)
    court_name = models.CharField(max_length=50)

    # 매치 성별 선택
    GENDER_CHOICES = [
        ("여성", "여성"),
        ("남성", "남성"),
        ("혼성", "혼성"),
    ]
    gender = models.CharField(
        max_length=2, choices=GENDER_CHOICES, null=True, blank=True
    )
    members_count = models.PositiveIntegerField()
    level = models.CharField(max_length=4)
    status = models.CharField(max_length=10, default="모집중")

    def __str__(self):
        return f"{self.team} - {self.date} {self.time} at {self.court_name}"

    def join_match(self, team):
        if self.team_vs is None:
            self.team_vs = team
            self.status = "모집 마감"
            self.save()
            return True
        return False


# 경기 결과
class MatchResult(models.Model):
    team = models.ForeignKey(
        "team.Team",
        related_name="results",
        on_delete=models.SET_NULL,
        null=True,
    )
    opponent = models.ForeignKey(
        "team.Team",
        related_name="opponent_results",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    date = models.DateField()
    result = models.CharField(
        max_length=1, choices=[("W", "Win"), ("D", "Draw"), ("L", "Lose")]
    )
    # 득점
    goals_for = models.IntegerField()
    # 실점
    goals_against = models.IntegerField()

    # 비디오파일 업로드
    video_file_left = models.FileField(
        upload_to="analysis/files/%Y/%m/%d/left/", null=True, blank=True
    )
    video_file_right = models.FileField(
        upload_to="analysis/files/%Y/%m/%d/right/", null=True, blank=True
    )

    # 경기 리포트 작성한 사람
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="match_results", on_delete=models.CASCADE
    )

    # 경기 참여한 멤버들
    players = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="match_results_players", blank=True
    )

    class Meta:
        ordering = ["date"]

    @property
    def goal_difference(self):
        return self.goals_for - self.goals_against

    @property
    def points(self):
        if self.result == "W":
            return 3
        elif self.result == "D":
            return 1
        else:
            return 0

    def __str__(self):
        return f"{self.team.team_name} vs {self.opponent.team_name} on {self.date}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        update_team_ranking(self.team)
        update_opponent_ranking(self)

        # Create or update the opponent's MatchResult


# 팀 순위 갱신
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


# 상대팀 순위 갱신
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


# *관계 : 기본 User - Teamboard - BoardComment
# 게시판 클래스
class Teamboard(models.Model):
    team = models.ForeignKey(
        "team.Team", on_delete=models.CASCADE, related_name="boards"
    )
    # User 기본 테이블에 사용자가 지워지면 Post 데이터도 지워짐. 1(User):N(Teamboard)관계
    createUser = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    boardTitle = models.CharField(max_length=50)  # 게시글 제목
    boardContent = models.TextField()  # 게시글 내용
    boardImg = models.ImageField(blank=True, null=True)  # 첨부파일
    createDate = models.DateTimeField(auto_now_add=True)  # 등록일
    updateDate = models.DateField(auto_now=True)  # 수정일
    viewCnt = models.IntegerField(default=0)  # 조회수
    commentCnt = models.IntegerField(default=0)  # 댓글수

    def __str__(self):
        return f"{self.pk}번째 등록글 : {self.boardTitle} (등록일 : {self.createDate})"

    # Teamboard 클래스내 속성은 3가지 임 : 댓글 > 참석 개수 카운팅, 불참석 개수 카운팅, 보류 개수 카운팅. 이 속성은 상세보기에서 게시글 별 참석현황 표시를 위해 사용
    @property
    def attend_count(self):
        return self.comments.filter(attendStatus=0).count()

    @property
    def absent_count(self):
        return self.comments.filter(attendStatus=1).count()

    @property
    def pending_count(self):
        return self.comments.filter(attendStatus=2).count()


# 댓글 게시판
class BoardComment(models.Model):
    ATTEND_CHOICES = [
        (0, "참석"),
        (1, "불참석"),
        (2, "보류"),
    ]
    # Teamboard 테이블 > 등록 게시글이 지워지면 댓글 데이터도 지워짐. 1(Teamboard):N(댓글)관계
    teamboard = models.ForeignKey(
        "team.Teamboard", on_delete=models.CASCADE, related_name="comments"
    )  # 게시물
    # User 기본 테이블에 사용자가 지워지면 Post 데이터도 지워짐. 1(User):N(Teamboard)관계
    commentUser = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )  # 등록자
    commentMsg = models.CharField(max_length=150, blank=True, null=True)  # 댓글내용
    attendStatus = models.SmallIntegerField(
        default=2
    )  # 참석여부 0:출석 1:미출석 2:보류
    createDate = models.DateTimeField(auto_now_add=True)  # 댓글 등록일
    updateDate = models.DateField(auto_now=True)  # 댓글 수정일

    def __str__(self):
        return f"{self.teamboard} 의 {self.pk}번째 댓글 : {self.commentMsg}(등록자 : {self.commentUser})"

    def get_attend_status_display(self):
        return dict(BoardComment.ATTEND_CHOICES).get(self.attendStatus, "Unknown")
