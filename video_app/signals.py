from .models import VideoModel
from .tasks import generate_hls_variants
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
import django_rq
import os

@receiver(post_save, sender=VideoModel)
def video_post_save(sender, instance, created, **kwargs):
    if created:
        print("New video created")
        queue = django_rq.get_queue('default', autocommit=True)
        queue.enqueue(generate_hls_variants, instance.video_file.path)

@receiver(post_delete, sender=VideoModel)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    if instance.video_file:
        if os.path.isfile(instance.video_file.path):
            os.remove(instance.video_file.path)