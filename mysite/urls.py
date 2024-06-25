import debug_toolbar
from django.apps import apps
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("accounts.urls", namespace="accounts")),
    path("team/", include("team.urls")),
    path("core/", include("core.urls")),
    path("chatbot/", include("chatbot.urls")),
    path("chat/", include("chat.urls")),
]

if apps.is_installed("debug_toolbar"):
    urlpatterns += [
        path("__debug__/", include(debug_toolbar.urls)),
    ]

# 이미지 파일 경로 받기
# static 함수는 settings의 debug설정이 참일때만 동작함
# static은 개발편의성을 위해 정적파일 서빙 기능을 제공
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
