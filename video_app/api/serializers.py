from rest_framework import serializers
from video_app.models import VideoModel

class VideoSerializer(serializers.ModelSerializer):
    """Serializer to interact with videos an containing fileds."""

    class Meta:
        model = VideoModel
        fields = ["id", "created_at", "title", "description", "thumbnail", "category", "video_file"]
        read_only_fields = ["id", "created_at"]
        extra_kwargs = {
            "thumbnail": {"required": True, "allow_null": False},
            "video_file": {"required": True, "allow_null": False},
        }

class SingleVideoSerializer(serializers.ModelSerializer):
    """Serializer to interact with singel videos and containig fields."""

    class Meta:
        model = VideoModel
        fields = ["id", "created_at", "title", "description", "thumbnail", "category", "video_file"]
        extra_kwargs = {
            "thumbnail": {"required": True, "allow_null": False},
            "video_file": {"required": True, "allow_null": False},
        }
        