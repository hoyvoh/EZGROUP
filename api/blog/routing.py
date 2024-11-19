from django.urls import re_path
from .consumers import CommentConsumer, NotificationConsumer

websocket_urlpatterns = [
    re_path(r'ws/comments/(?P<post_id>\d+)/$', CommentConsumer.as_asgi()),
    re_path(r'ws/notifications/$', NotificationConsumer.as_asgi()),
]
