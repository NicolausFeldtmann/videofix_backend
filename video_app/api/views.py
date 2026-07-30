from django.http import FileResponse, Http404, HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response

from video_app.models import VideoModel
from .serializers import VideoSerializer, SingleVideoSerializer
from .services import (
    ensure_hls_for_resolution,
    ensure_hls_variants_queued,
    build_master_playlist_lines,
    is_supported_resolution,
    get_playlist_or_enqueue,
    get_hls_segment_path
)

class VideoListCreateView(generics.ListCreateAPIView):
    """View to handle video-list. And grant permissions, depending of user role."""

    queryset = VideoModel.objects.all()
    serializer_class = VideoSerializer

    def get_permissions(self):
        """Gives admin permission for POST-requests."""

        if self.request.method == "POST":
            return [IsAdminUser()]
        return [IsAuthenticated()]

class SingleVideoView(generics.RetrieveUpdateDestroyAPIView):
    """View to interact with single video."""

    queryset = VideoModel.objects.all()
    serializer_class = SingleVideoSerializer

    def get_permissions(self):
        """Gives admin permission fot DELETE-requests."""

        if self.request.methos == "DELETE":
            return [IsAdminUser()]
        return [IsAuthenticated]

class VideoHLSPlaylistView(APIView):
    """View to handle GET request."""

    permission_classes = [IsAuthenticated]

    def get(self, request, movie_id, resolution):
        """Checks if video object exists and has suported resolution"""
        """Returns playlsit-file via FileResponse as soon as ready."""
        """Else returns status 200."""

        video = get_object_or_404(VideoModel, pk=movie_id)

        if not video.video_file:
            raise Http404("Video file not available.")

        if not is_supported_resolution(resolution):
            return Response({"detail": "Unsuported resolution."}, status=status.HTTP_400_BAD_REQUEST)

        playlist = get_playlist_or_enqueue(video, resolution)
        if playlist:
            return FileResponse(open(playlist, "rb"), content_type="application/vnd.apple.mpegutl",)

        return Response({"detail": "HLS playlist generation started."}, status=status.HTTP_200_OK)

class VideoHLSSegmentView(APIView):
    """View to handle GET request"""

    permission_classes = [IsAuthenticated]

    def get(self, request, movie_id, resolution, segment):
        """Returns path of segment-file as soon as ready."""
        """Returns status 200."""

        video = get_object_or_404(VideoModel, pk=movie_id)

        if not video.video_file:
            raise Http404("Video file not available.")

        if not is_supported_resolution(resolution):
            return Response({"detail": "Invalid segment path"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            segment_path = get_hls_segment_path(video, resolution, segment)
        except ValueError:
            return Response({"detail": "Invalid segment path"}, status=status.HTTP_400_BAD_REQUEST)

        if segment_path.exists():
            return FileResponse(open(segment_path, "rb"), content_type="video/MP2T")

        playlist_ready = ensure_hls_for_resolution(video, resolution)
        if not playlist_ready:
            return Response({"detail": "HLS generation started."}, status=status.HTTP_200_OK)

        return Response({"detail": "Segment available"}, status=status.HTTP_200_OK)

class VideoHLSMasterView(APIView):
    """View for GET requests of master m3u8"""

    permission_classes = [IsAuthenticated]

    def get(self, request, movie_id):
        """Creates and retruns master playlist contents."""

        video = get_object_or_404(VideoModel, pk=movie_id)

        if not video.video_file:
            raise Http404("Video file not available.")

        ensure_hls_variants_queued(video)

        lines = build_master_playlist_lines(video, request)
        content = "\n".join(lines) + "\n"
        return HttpResponse(content, content_type="application/vnd.apple.mpegurl")