from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from video_app.models import VideoModel
from .serializers import VideoSerializer

class VideoListCreateView(generics.ListCreateAPIView):
    queryset = VideoModel.objects.all()
    serializer_class = VideoSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return[IsAdminUser()]
        return [AllowAny()]