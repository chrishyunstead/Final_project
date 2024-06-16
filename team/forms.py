import os

from PIL import Image
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Submit, Row, Column, HTML
from django import forms
from django.core.files import File
from django.core.files.base import ContentFile

from accounts.models import SiggAreas
from .models import Team, Court


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
