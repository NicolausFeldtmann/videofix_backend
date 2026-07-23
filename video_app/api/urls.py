from django.urls import path
from .views import VideoListCreateView, SingleVideoView, VideoHLSPlaylistView, VideoHLSSegmentView, VideoHLSMasterView

urlpatterns = [
    path('video/', VideoListCreateView.as_view(), name='video-list'),
    path('video/<int:movie_id>/<str:resolution>/index.m3u8', VideoHLSPlaylistView.as_view(), name='video-hls-playlist'),
    path('video/<int:pk>/', SingleVideoView.as_view(), name='video-detail'),
    path('video/<int:movie_id>/<str:resolution>/<str:segment>/', VideoHLSSegmentView.as_view(), name='video-hls-segment'),
    path('video/<int:movie_id>/master.m3u8', VideoHLSMasterView.as_view(), name='video-hls-master')
]
