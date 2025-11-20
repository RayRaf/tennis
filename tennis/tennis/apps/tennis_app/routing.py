from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/friendly_game/(?P<club_id>\d+)/$', consumers.FriendlyGameConsumer.as_asgi()),
]
