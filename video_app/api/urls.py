from django.urls import path
from .views import VideoListCreateView

urlpatterns = [
    path('video/', VideoListCreateView.as_view(), name='video-list')
]