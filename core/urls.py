from django.urls import path
from django.views.generic import TemplateView

from . import views

app_name = "core"

urlpatterns = [
    path("", TemplateView.as_view(template_name="accounts/main.html"), name="main"),
]
