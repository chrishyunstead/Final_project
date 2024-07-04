from django.urls import path
from django.views.generic import TemplateView

from . import views

app_name = "chatbot"

urlpatterns = [
    path("", views.chatbot, name="chatbot"),
]
