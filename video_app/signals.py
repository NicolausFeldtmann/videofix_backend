from .models import VideoModel
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
import os

@receiver(post_save, sender=VideoModel)
def video_post_save(sender, instance, created, **kwargs):
    if created:
        print("New video created")

@receiver(post_delete, sender=VideoModel)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    if instance.video_file:
        if os.path.isfile(instance.video_file.path):
            os.remove(instance.video_file.path)