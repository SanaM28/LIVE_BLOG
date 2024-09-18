

# routing.py

from django.urls import re_path
from blog import consumers

websocket_urlpatterns = [
    re_path(r'ws/blog/$', consumers.BlogConsumer.as_asgi()),
]
