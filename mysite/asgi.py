import os
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application

# 실시간 채팅 구현하려다 잘 안됨
# import chat.routing
# from chat.routing import websocket_urlpatterns


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")
django_asgi_app = get_asgi_application()
# 클라이언트와 Channels 개발 서버가 연결 될 때, 어느 protocol 타입의 연결인지
#
# application = ProtocolTypeRouter(
#     {
#         "http": django_asgi_app,
#         # (http->django views is added by default)
#         # 만약에 websocket protocol 이라면, AuthMiddlewareStack
#         "websocket": AllowedHostsOriginValidator(
#             AuthMiddlewareStack(chat.routing.websocket_urlpatterns)
#             # URLRouter 로 연결, 소비자의 라우트 연결 HTTP path를 조사
#         ),
#     }
# )
