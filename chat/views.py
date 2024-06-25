from django.shortcuts import render


# 팀 채팅 입장페이지
def index(request):
    return render(request, "chat/index.html")


def room(request, room_name):
    return render(request, "chat/room.html", {"room_name": room_name})
