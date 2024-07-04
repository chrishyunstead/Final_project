import os

from PIL import Image
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Submit, Row, Column, HTML
from django import forms
from django.core.files import File
from django.core.files.base import ContentFile
from django.db.models import Q

from accounts.models import SiggAreas, User
from .models import Team, Court, Match, MatchResult, Teamboard, BoardComment


class TeamForm(forms.ModelForm):
    DAYS_OF_WEEK = [
        ("월", "월"),
        ("화", "화"),
        ("수", "수"),
        ("목", "목"),
        ("금", "금"),
        ("토", "토"),
        ("일", "일"),
    ]

    TIMES_OF_DAY = [
        ("아침", "아침 6-10시"),
        ("낮", "낮 10-18시"),
        ("저녁", "저녁 18-24시"),
        ("심야", "심야 24-6시"),
    ]

    AGE_GROUPS = [
        ("10대", "10대"),
        ("20대", "20대"),
        ("30대", "30대"),
        ("40대", "40대"),
        ("50대", "50대"),
        ("60대", "60대"),
        ("70대", "70대"),
        ("80대", "80대"),
    ]

    GENDERS = [
        ("여성", "여성"),
        ("남성", "남성"),
        ("혼성", "혼성"),
    ]

    team_name = forms.CharField(
        max_length=10,
        required=True,
        widget=forms.TextInput(attrs={"placeholder": "최대 10자"}),
    )
    team_image_url = forms.ImageField(
        required=False, widget=forms.ClearableFileInput(attrs={"class": "form-control"})
    )
    team_day = forms.MultipleChoiceField(
        choices=DAYS_OF_WEEK,
        widget=forms.CheckboxSelectMultiple,
        required=True,
    )
    team_timeslot = forms.ChoiceField(
        choices=TIMES_OF_DAY,
        widget=forms.RadioSelect,
        required=True,
    )

    team_ages = forms.ChoiceField(
        choices=AGE_GROUPS,
        widget=forms.RadioSelect,
        required=True,
        label="주요 나이대",
    )

    gender = forms.ChoiceField(
        choices=GENDERS,
        widget=forms.RadioSelect,
        required=True,
        label="성별",
    )

    sido_name = forms.ChoiceField(
        choices=[
            (sido, sido)
            for sido in SiggAreas.objects.values_list("sido_name", flat=True).distinct()
        ],
        required=True,
        label="도시",
    )
    sigg_name = forms.ChoiceField(
        choices=[(sigg.sigg_name, sigg.sigg_name) for sigg in SiggAreas.objects.all()],
        required=True,
        label="지역구",
    )
    court_name = forms.ChoiceField(
        choices=[
            (court, court)
            for court in Court.objects.values_list("court_name", flat=True).distinct()
        ],
        required=False,
        label="주 활동구장",
    )

    def save(self, commit=True):
        team = super().save(commit=False)
        if commit:
            team.save()
            team.members.add(team.created_by)  # 팀장 멤버 추가
        return team

    class Meta:
        model = Team
        fields = [
            "team_name",
            "team_image_url",
            "team_day",
            "team_timeslot",
            "team_ages",
            "gender",
            "sido_name",
            "sigg_name",
            "court_name",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.form_enctype = "multipart/form-data"
        self.helper.layout = Layout(
            HTML("<h4>팀의 기본 정보를 입력하세요</h4>"),
            Row(
                Column(
                    Field("team_name", css_class="form-control"),
                    css_class="form-group col-md-6 mb-0",
                ),
                Column(
                    Field("team_image_url", css_class="form-control"),
                    css_class="form-group col-md-6 mb-0",
                ),
                css_class="form-row",
            ),
            HTML("<h4>팀의 활동 정보를 입력하세요</h4>"),
            Field("team_day", css_class="form-check-inline"),
            Field("team_timeslot", css_class="form-check-inline"),
            HTML("<h4>팀의 지역 정보를 입력하세요</h4>"),
            Row(
                Column(
                    Field("sido_name", css_class="form-select"),
                    css_class="form-group col-md-4 mb-0",
                ),
                Column(
                    Field("sigg_name", css_class="form-select"),
                    css_class="form-group col-md-4 mb-0",
                ),
                Column(
                    Field("court_name", css_class="form-select"),
                    css_class="form-group col-md-4 mb-0",
                ),
                css_class="form-row",
            ),
            HTML("<h4>팀의 인원 정보를 입력하세요</h4>"),
            Field("team_ages", css_class="form-check-inline"),
            Field("gender", css_class="form-check-inline"),
            Submit("submit", "팀 생성하기", css_class="btn btn-primary"),
        )

    def clean_team_image_url(self):
        team_image_url: File = self.cleaned_data.get("team_image_url")
        if team_image_url:
            img = Image.open(team_image_url)
            MAX_SIZE = (512, 512)
            img.thumbnail(MAX_SIZE)
            img = img.convert("RGB")

            thumb_name = os.path.splitext(team_image_url.name)[0] + ".jpg"

            thumb_file = ContentFile(b"", name=thumb_name)
            img.save(thumb_file, format="jpeg")

            return thumb_file

        return team_image_url


class MatchForm(forms.ModelForm):
    date = forms.DateField(
        label="경기 날짜",
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}),
    )
    time = forms.TimeField(
        label="경기 시간",
        widget=forms.TimeInput(attrs={"type": "time", "class": "form-control"}),
    )
    gender = forms.ChoiceField(
        label="성별",
        choices=Match.GENDER_CHOICES,
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    level = forms.ChoiceField(
        choices=[
            ("풋린이", "풋린이"),
            ("풋내기", "풋내기"),
            ("풋아마", "풋아마"),
            ("풋현역", "풋현역"),
            ("풋롱도르", "풋롱도르"),
        ],
        required=True,
        widget=forms.RadioSelect,
        label="팀 수준",
    )
    sido_name = forms.ChoiceField(
        choices=[
            (sido, sido)
            for sido in SiggAreas.objects.values_list("sido_name", flat=True).distinct()
        ],
        required=True,
        label="도시",
    )
    sigg_name = forms.ChoiceField(
        choices=[(sigg.sigg_name, sigg.sigg_name) for sigg in SiggAreas.objects.all()],
        required=True,
        label="지역구",
    )
    court_name = forms.ChoiceField(
        choices=[
            (court, court)
            for court in Court.objects.values_list("court_name", flat=True).distinct()
        ],
        required=True,
        label="주 활동구장",
    )
    members_count = forms.IntegerField(
        label="참여 인원",
        min_value=1,  # 최소값 설정
        required=True,  # 필수 입력 필드로 설정
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",  # Bootstrap 클래스를 추가하여 스타일 지정
                "placeholder": "참여 인원을 입력하세요",  # 입력 필드에 플레이스홀더 추가
            }
        ),
    )

    class Meta:
        model = Match
        fields = [
            "date",
            "time",
            "sido_name",
            "sigg_name",
            "court_name",
            "gender",
            "members_count",
            "level",
        ]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "time": forms.TimeInput(attrs={"type": "time"}),
        }


class MatchResultForm(forms.ModelForm):
    date = forms.ChoiceField(choices=[], required=True, label="경기 날짜")
    opponent = forms.ModelChoiceField(
        queryset=Team.objects.none(), required=True, label="상대팀"
    )
    video_file_left = forms.FileField(required=False, label="왼쪽 비디오 파일")
    video_file_right = forms.FileField(required=False, label="오른쪽 비디오 파일")

    class Meta:
        model = MatchResult
        fields = [
            "date",
            "opponent",
            "result",
            "goals_for",
            "goals_against",
            "video_file_left",
            "video_file_right",
        ]

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if user:
            # 작성된 경기 날짜 제외
            written_dates = MatchResult.objects.values_list("date", flat=True)
            matches = (
                Match.objects.filter(
                    (Q(team__created_by=user) | Q(team_vs__created_by=user))
                    & Q(status="모집 마감")
                )
                .exclude(date__in=written_dates)
                .distinct()
            )
            self.fields["date"].choices = [
                (match.date, match.date) for match in matches
            ]
            self.fields["opponent"].queryset = Team.objects.filter(
                Q(pk__in=matches.values_list("team", flat=True))
                | Q(pk__in=matches.values_list("team_vs", flat=True))
            ).distinct()


class MatchResultEditForm(forms.ModelForm):
    date = forms.ChoiceField(choices=[], required=True, label="경기 날짜")
    opponent = forms.ModelChoiceField(
        queryset=Team.objects.none(), required=True, label="상대팀"
    )
    video_file_left = forms.FileField(required=False, label="왼쪽 비디오 파일")
    video_file_right = forms.FileField(required=False, label="오른쪽 비디오 파일")

    class Meta:
        model = MatchResult
        fields = [
            "date",
            "opponent",
            "result",
            "goals_for",
            "goals_against",
            "video_file_left",
            "video_file_right",
        ]

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if user:
            # 작성된 경기 날짜 포함
            written_dates = MatchResult.objects.filter(created_by=user).values_list(
                "date", flat=True
            )
            matches = Match.objects.filter(
                Q(team__created_by=user) | Q(team_vs__created_by=user),
                date__in=written_dates,
                status="모집 마감",
            ).distinct()
            self.fields["date"].choices = [
                (match.date, match.date) for match in matches
            ]
            self.fields["opponent"].queryset = Team.objects.filter(
                Q(pk__in=matches.values_list("team", flat=True))
                | Q(pk__in=matches.values_list("team_vs", flat=True))
            ).distinct()


# 경기날짜 선택 폼
class DateSelectForm(forms.Form):
    date = forms.ChoiceField(choices=[], required=True, label="날짜 선택")

    def __init__(self, *args, **kwargs):
        match_dates = kwargs.pop("match_dates", [])
        super().__init__(*args, **kwargs)
        self.fields["date"].choices = [(date, date) for date in match_dates]


class MemberSelectForm(forms.Form):
    members = forms.ModelMultipleChoiceField(
        queryset=User.objects.none(),
        required=True,
        label="경기 뛴 멤버",
        widget=forms.CheckboxSelectMultiple,
    )

    def __init__(self, *args, **kwargs):
        team_members = kwargs.pop("team_members", None)
        super().__init__(*args, **kwargs)
        if team_members:
            self.fields["members"].queryset = team_members
            self.fields["members"].label_from_instance = lambda obj: obj.username


class TeamBoardForm(forms.ModelForm):
    class Meta:
        model = Teamboard
        fields = ["boardTitle", "boardContent", "boardImg"]

    def __init__(self, *args, **kwargs):
        super(TeamBoardForm, self).__init__(*args, **kwargs)
        self.fields["boardImg"].required = False  # 이미지 필드를 선택 사항으로 설정

    def clean_team_image_url(self):
        boardImg: File = self.cleaned_data.get("boardImg")
        if boardImg:
            img = Image.open(boardImg)
            MAX_SIZE = (512, 512)
            img.thumbnail(MAX_SIZE)
            img = img.convert("RGB")

            thumb_name = os.path.splitext(boardImg.name)[0] + ".jpg"

            thumb_file = ContentFile(b"", name=thumb_name)
            img.save(thumb_file, format="jpeg")

            return thumb_file

        return boardImg


# 게시글에 대한 댓글 등록폼 : models.py > BoardComment에서 사용자로부터 받을 필드만 별도 추출 및 저장
# 선택 항목으로, 라디오 버튼을 통해 "참석", "불참석", "보류" 중 하나를 선택
class BoardCommentForm(forms.ModelForm):
    ATTEND_CHOICES = [(0, "참석"), (1, "불참석"), (2, "보류")]
    attendStatus = forms.ChoiceField(
        choices=ATTEND_CHOICES, widget=forms.RadioSelect, label="참석 여부"
    )

    class Meta:
        model = BoardComment
        fields = ["commentMsg", "attendStatus"]
