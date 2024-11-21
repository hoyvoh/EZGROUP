from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from authen.models import User
from django.contrib.auth.models import AnonymousUser

# class UserSession(models.Model):
#     session_token = models.CharField(max_length=255, unique=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     is_anonymous = models.BooleanField(default=True)
#     '''
#     user_id = models.TextField()
#     user_name = models.CharField(max_length=255, blank=True)
#     user_email = models.EmailField(max_length=255, blank=True)
#     '''

#     def __str__(self):
#         if self.user:
#             return f"Session for {self.user.email}"
#         return "Anonymous Session"
    
#     class Meta:
#         managed = True

# author_session = models.ForeignKey(
    #     UserSession,
    #     on_delete=models.PROTECT, 
    #     related_name="posts"
    # )
    # author_name = models.CharField(max_length=255, blank=True) 
    # author_email = models.EmailField(max_length=255, blank=True) 

class Post(models.Model):
    title = models.CharField(max_length=255, null=False)
    content = models.TextField(null=False)
    category = models.CharField(max_length=255)
    user_id = models.CharField(max_length=255,null=False, default="default")
    user_name = models.CharField(max_length=255,null=False, default="default")
    user_email = models.EmailField(max_length=255, null=False, default="default@email.com")
    created_at = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Post: {self.title} | by {self.author_name or "Anonymous"}'
    class Meta:
        managed = True
    
class Image(models.Model):
    post = models.ForeignKey('Post', related_name='images', on_delete=models.CASCADE, null=True)
    image_url = models.URLField(null=False)
    label = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.label if self.label else f"Image for {self.post.title}"
    class Meta:
        managed = True

# Managed by consumers
class Comment(models.Model):
    post = models.ForeignKey('Post', on_delete=models.CASCADE, related_name="comments", null=False)
    content = models.TextField(null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    user_id = models.CharField(max_length=255,null=False, default="default")
    user_name = models.CharField(max_length=255,null=False, default="default")
    user_email = models.EmailField(max_length=255, null=False, default="default@email.com")

    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')

    def __str__(self):
        return f"Comment by {self.commenter_name}"

    class Meta:
        managed = True

    
class Like(models.Model):
    user_id = models.CharField(max_length=255,null=False, default="default")
    user_name = models.CharField(max_length=255,null=False, default="default")
    user_email = models.EmailField(max_length=255, null=False, default="default@email.com")
    post = models.ForeignKey('Post', on_delete=models.CASCADE, related_name="likes", null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ('user_id', 'post')
        managed = True

    def __str__(self):
        return f"{self.user_name} likes {self.post.title}"

class Notification(models.Model):
    user_id = models.CharField(max_length=255,null=False, default="default")
    user_name = models.CharField(max_length=255,null=False, default="default")
    user_email = models.EmailField(max_length=255, null=False, default="default@email.com")
    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user_name}: {self.message}"
    class Meta:
        managed = True
    
