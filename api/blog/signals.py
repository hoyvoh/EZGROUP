from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Like, Share, Comment, Notification

# Trigger notification when a post is liked
@receiver(post_save, sender=Like)
def create_like_notification(sender, instance, created, **kwargs):
    if created:
        post = instance.post
        user = post.author_session.user
        if user != instance.user:  # Don't notify if the user liked their own post
            Notification.objects.create(
                user=user,
                message=f"{instance.user.username} liked your post: '{post.title}'"
            )

# Trigger notification when a post is shared
@receiver(post_save, sender=Share)
def create_share_notification(sender, instance, created, **kwargs):
    if created:
        post = instance.post
        user = post.author_session.user
        if user != instance.user:
            Notification.objects.create(
                user=user,
                message=f"{instance.user.username} shared your post: '{post.title}'"
            )

# Trigger notification when a comment is created
@receiver(post_save, sender=Comment)
def create_comment_notification(sender, instance, created, **kwargs):
    if created:
        post = instance.post
        user = post.author_session.user
        if user != instance.author:
            Notification.objects.create(
                user=user,
                message=f"{instance.author.username} commented on your post: '{post.title}'"
            )
