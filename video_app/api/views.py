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
    resolve_segment_path,
    build_master_playlist_lines,
    is_supported_resolution,
    get_playlist_or_enqueue,
)

class VideoListCreateView(generics.ListCreateAPIView):
    queryset = VideoModel.objects.all()
    serializer_class = VideoSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAdminUser()]
        return [IsAuthenticated()]

class SingleVideoView(generics.RetrieveUpdateDestroyAPIView):
    queryset = VideoModel.objects.all()
    serializer_class = SingleVideoSerializer

    def get_permissions(self):
        if self.request.methos == "DELETE":
            return [IsAdminUser()]
        return [IsAuthenticated]

class VideoHLSPlaylistView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, movie_id, resolution):
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
    permission_classes = [IsAuthenticated]

    def get(self, request, movie_id, resolution, segment):
        video = get_object_or_404(VideoModel, pk=movie_id)

        if not video.video_file:
            raise Http404("Video file not available.")

        if not is_supported_resolution(resolution):
            return Response({"detail": "Invalid segment path"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            segment_path = resolve_segment_path(video, resolution, segment)
        except ValueError:
            return Response({"detail": "Invalid segment path"}, status=status.HTTP_400_BAD_REQUEST)

        if segment_path.exists():
            return FileResponse(open(segment_path, "rb"), content_type="video/MP2T")

        playlist_ready = ensure_hls_for_resolution(video, resolution)
        if not playlist_ready:
            return Response({"detail": "HLS generation started."}, status=status.HTTP_200_OK)

        return Response({"detail": "Segment available"}, status=status.HTTP_200_OK)

class VideoHLSMasterView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, movie_id):
        video = get_object_or_404(VideoModel, pk=movie_id)

        if not video.video_file:
            raise Http404("Video file not available.")

        ensure_hls_variants_queued(video)

        lines = build_master_playlist_lines(video, request)
        content = "\n".join(lines) + "\n"
        return HttpResponse(content, content_type="application/vnd.apple.mpegurl")