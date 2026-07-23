from rest_framework import serializers
from video_app.models import VideoModel

class VideoSerializer(serializers.ModelSerializer):

    class Meta:
        model = VideoModel
        fields = ["id", "created_at", "titel", "description", "thumbnail_url", "category", "video_file"]
        read_only_fields = ["id", "created_at"]

class SingleVideoSerializer(serializers.ModelSerializer):

    class Meta:
        model = VideoModel
        fields = ["id", "created_at", "titel", "description", "thumbnail_url", "category", "video_file"]
        