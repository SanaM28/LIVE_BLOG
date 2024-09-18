# blog/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver

# from .models import Post
from django.apps import apps  # Import apps to use get_model
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


@receiver(post_save, sender="blog.Post")
def send_notification(sender, instance, created, **kwargs):
    Post = apps.get_model("blog", "Post")  # Get the Post model dynamically
    channel_layer = get_channel_layer()

    if created:
        message = f"New post created: {instance.title}"
    else:
        message = f"Post updated: {instance.title}"

    # Send the notification to all users
    async_to_sync(channel_layer.group_send)(
        "blog_updates", {"type": "notification", "data": message}
    )


# @receiver(post_save, sender="blog.Comment")
# def send_comment_notification(sender, instance, created, **kwargs):
#     if created:
#         channel_layer = get_channel_layer()
#         message = f'New comment on your post: "{instance.post.title}" by {instance.user.username}'

#         # Notify the post author
#         async_to_sync(channel_layer.group_send)(
#             "blog_updates",
#             {
#                 "type": "send_comment_notification",
#                 "message": message,
#                 "post_id": instance.post.id,
#             },
#         )
