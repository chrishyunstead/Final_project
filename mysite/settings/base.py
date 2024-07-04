import os
import sys
from pathlib import Path
from my_settings import SECRET, DATABASE
import pymysql

pymysql.install_as_MySQLdb()

from django.core.exceptions import ImproperlyConfigured
from django.urls import reverse_lazy

# Build paths inside the project like this: BASE_DIR / 'subdir'.


from environ import Env


BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = Env()

ENV_PATH = BASE_DIR / ".env"
if ENV_PATH.exists():
    with ENV_PATH.open(encoding="utf-8") as f:
        env.read_env(f, overwrite=True)
else:
    print("not found:", ENV_PATH, file=sys.stderr)


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env.str(
    "SECRET_KEY",
    default=SECRET,
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool("DEBUG", True)

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=[])
# ALLOWED_HOSTS = ["3.37.120.16"]

# Application definition

INSTALLED_APPS = [
    # django apps
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django_components.safer_staticfiles",
    "django.contrib.humanize",
    "django.contrib.syndication",
    "crispy_forms",
    "crispy_bootstrap5",
    "django_components",
    "django_extensions",
    "django_htmx",
    "rest_framework",
    "template_partials",
    "accounts",
    "core",
    "accounts.templatetags",
    "team",
    "chatbot",
    "channels",
    "widget_tweaks",
    "corsheaders",
]

# 팀채팅 구현
ASGI_APPLICATION = "mysite.asgi.application"

# 팀채팅 로컬에서 실행될 수 있게
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("172.17.0.2", 6379)],
        },
    },
}

# if DEBUG:
#     INSTALLED_APPS += [
#         "debug_toolbar",
#     ]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django_htmx.middleware.HtmxMiddleware",
]


CORS_ALLOWED_ORIGINS = [
    "http://43.200.89.250:8080",
    "http://43.200.89.250",
    # "http://43.200.89.250:8080/query",
]
CSRF_TRUSTED_ORIGINS = [
    "http://43.200.89.250:8080",
    "http://43.200.89.250",
    "http://43.200.89.250:8080/query",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]


CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True
SECURE_CROSS_ORIGIN_OPENER_POLICY = None


# # CORS 설정
# CORS_ALLOW_ALL_ORIGINS = True
# CORS_ALLOW_CREDENTIALS = True

# 특정 Origin만 허용하려면 다음과 같이 설정
# CORS_ALLOWED_ORIGINS = [
#     "http://13.209.235.183",
# ]
# # CSRF 설정
# CSRF_COOKIE_SECURE = True
# SESSION_COOKIE_SECURE = True


# CORS_ORIGIN_ALLOW_ALL = True
#
# CORS_ALLOW_CREDENTIALS = True  # 인증 정보를 포함할지 여부

# if DEBUG:
#     MIDDLEWARE = [
#         "debug_toolbar.middleware.DebugToolbarMiddleware",
#     ] + MIDDLEWARE


ROOT_URLCONF = "mysite.urls"


TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            BASE_DIR / "templates",
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "mysite.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

# CSRF 설정
# CSRF_TRUSTED_ORIGINS = ["http://localhost:8000", "http://127.0.0.1:8000"]


DATABASES = DATABASE

AUTH_USER_MODEL = "accounts.User"

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = env.str("LANGUAGE_CODE", "ko-kr")

TIME_ZONE = "Asia/Seoul"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

# STATIC_URL = "static/"
#
# STATICFILES_DIRS = [
#     BASE_DIR / "core" / "src-django-components",
# ]
#
#
# MEDIA_URL = "/media/"
#
# MEDIA_ROOT = BASE_DIR / "media"

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATICFILES_DIRS = [
    BASE_DIR / "core" / "src-django-components",
]
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
# CORS 설정
# CORS_ORIGIN_ALLOW_ALL = True

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

INTERNAL_IPS = env.list("INTERNAL_IPS", default=["127.0.0.1"])

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"

CRISPY_TEMPLATE_PACK = "bootstrap5"

COMPONENTS = {
    "slot_context_behavior": "allow_override",
}

# Email
# https://docs.djangoproject.com/en/4.2/topics/email/#smtp-backend
# (장고 기본 기능) 메일 발송 테스트: python manage.py sendtestemail 수신자_이메일

EMAIL_HOST = env.str("EMAIL_HOST", default=None)

if DEBUG and EMAIL_HOST is None:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
else:
    try:
        EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
        EMAIL_PORT = env.int("EMAIL_PORT")
        EMAIL_USE_SSL = env.bool("EMAIL_USE_SSL", default=False)
        EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS", default=False)
        EMAIL_HOST_USER = env.str("EMAIL_HOST_USER")
        EMAIL_HOST_PASSWORD = env.str("EMAIL_HOST_PASSWORD")
        DEFAULT_FROM_EMAIL = env.str("DEFAULT_FROM_EMAIL")
    except ImproperlyConfigured as e:
        print("ERROR:", e, file=sys.stderr)
        EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

REST_FRAMEWORK = {
    #     # Use Django's standard `django.contrib.auth` permissions,
    #     # or allow read-only access for unauthenticated users.
    #     "DEFAULT_PERMISSION_CLASSES": [
    #         "rest_framework.permissions.AllowAny",
    #     ]
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
        # "core.renderers.PandasXlsxRenderer",
        # "core.renderers.WordcloudRenderer",
    ],
    "PAGE_SIZE": env.int("REST_FRAMEWORK_PAGE_SIZE", 5),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
}
# 이거 설정해야지 로그인 장식자가 적용돼서 로그인 안 한 사람이 접근하려고 하면 로그인페이지로 넘김
LOGIN_URL = "accounts:login"

LOGIN_REDIRECT_URL = reverse_lazy("accounts:main")

from django.contrib.messages import constants as messages_constants  # noqa


if DEBUG:
    MESSAGE_LEVEL = messages_constants.DEBUG


ADMIN_PREFIX = os.environ.get("ADMIN_PREFIX", "secret-admin/")

# 템플릿 파일이 노란줄로 안읽힘
# TEMPLATE_LOADERS = (
#     "django.template.loaders.filesystem.Loader",
#     "django.template.loaders.app_directories.Loader",
# )


# # 세션 엔진 설정 (기본값은 데이터베이스 세션)(chatbot앱 세션 설정)
# SESSION_ENGINE = "django.contrib.sessions.backends.db"
#
# # 세션 만료 설정 (기본값은 브라우저가 닫힐 때 세션 만료)
# SESSION_EXPIRE_AT_BROWSER_CLOSE = False
#
# # 세션 만료 시간 설정 (예: 30분 동안 활동이 없으면 세션 만료)
# SESSION_COOKIE_AGE = 1800  # 30분 (1800초)
