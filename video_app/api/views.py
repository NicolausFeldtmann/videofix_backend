from django.http import FileResponse, Http404, HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from video_app.models import VideoModel
from video_app.tasks import generate_hls
from .serializers import VideoSerializer, SingleVideoSerializer
import django_rq

class VideoListCreateView(generics.ListCreateAPIView):
    queryset = VideoModel.objects.all()
    serializer_class = VideoSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAdminUser()]
        return [AllowAny()]

class SingleVideoView(generics.RetrieveUpdateDestroyAPIView):
    queryset = VideoModel.objects.all()
    serializer_class = SingleVideoSerializer

    def get_permissions(self):
        if self.request.method == "DELETE":
            return [IsAdminUser()]
        return [AllowAny()]

class VideoHLSPlaylistView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, movie_id, resolution):
        video = get_object_or_404(VideoModel, pk=movie_id)

        if not video.video_file:
            raise Http404("Video file not available.")

        if resolution not in VideoModel.HLS_RESOLUTIONS:
            return Response(
                {"detail": "Unsupported resolution"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        playlist_path = video.get_hls_playlist_path(resolution)

        if playlist_path and playlist_path.exists():
            return FileResponse(
                open(playlist_path, "rb"), 
                content_type="application/vnd.apple.mpegurl"
            )

        queue = django_rq.get_queue("default")
        queue.enqueue(generate_hls, video.video_file.path, resolution)

        return Response(
            {"detail": "HLS playlist generation started, try again later."},
            status=status.HTTP_202_ACCEPTED,
        )

class VideoHLSSegmentView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, movie_id, resolution, segment):
        video = get_object_or_404(VideoModel, pk=movie_id)

        if not video.video_file:
            raise Http404("Video file not available.")

        if resolution not in VideoModel.HLS_RESOLUTIONS:
            return Response(
                {"detail": "Unsuported resolution"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            segment_path = video.get_hls_segment_path(resolution, segment)
        except ValueError:
            return Response(
                {"detail": "Invalid segment path"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if segment_path.exists():
            return FileResponse(
                open(segment_path, "rb"),
                content_type="video/MP2T"
            )

        playlist_path = video.get_hls_playlist_path(resolution)

        if not (playlist_path and playlist_path.exists()):
            queue = django_rq.get_queue("default")
            queue.enqueue(generate_hls, video.video_file.path, resolution)
            return Response(
                {"detail": "HLS generation started. Try again later"},
                status=status.HTTP_202_ACCEPTED
            )
        return Response(
            {"detail": "Segment not yet available, try again later."},
            status=status.HTTP_202_ACCEPTED
        )

class VideoHLSMasterView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, movie_id):
        video = get_object_or_404(VideoModel, pk=movie_id)

        if not video.video_file:
            raise Http404("Video file not available.")

        queue = django_rq.get_queue("default")
        for resolution in VideoModel.HLS_RESOLUTIONS:
            playlist_path = video.get_hls_playlist_path(resolution)
            if not (playlist_path and playlist_path.exists()):
                queue.enqueue(generate_hls, video.video_file.path, resolution)

        lines = ["#EXTM3U"]
        for resolution, size in VideoModel.HLS_RESOLUTIONS.items():
            width, height = size.split("x")
            bandwidth = {
                "360p": 800000, 
                "480p": 1400000, 
                "720p": 2800000
            }.get(resolution, 1000000)
            playlist_url = request.build_absolute_uri(
                f"/video/{movie_id}/{resolution}/index.m3u8"
            )
            lines.append(
                f"#EXT-X-STREAM-INF:BANDWIDTH={bandwidth},RESOLUTION={width}x{height}"
            )
            lines.append(playlist_url)

        content = "\n".join(lines) + "\n"
        return HttpResponse(content, content_type="application/vnd.apple.mpegurl")