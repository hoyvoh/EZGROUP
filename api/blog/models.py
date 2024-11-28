from django.db import models
from django.conf import settings
import boto3

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
        return f'Post: {self.title} | by {self.user_name or "Anonymous"}'
    class Meta:
        managed = True
    
class Image(models.Model):
    post = models.ForeignKey('Post', related_name='images', on_delete=models.CASCADE, null=True)
    image_url = models.URLField(null=False)
    label = models.CharField(max_length=255, blank=True)

    def save(self, *args, **kwargs):
        if not self.label and self.post:
            self.label = f"Figure: {self.post.title}"
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.image_url:
            s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_REGION
            )
            bucket_name = settings.AWS_STORAGE_BUCKET_NAME
            file_key = self.image_url.replace(f'https://{settings.AWS_S3_CUSTOM_DOMAIN}/', '')
            s3_client.delete_object(Bucket=bucket_name, Key=file_key)

        super().delete(*args, **kwargs)

    def __str__(self):
        return self.label if self.label else f"Image for {self.post.title}"
    class Meta:
        managed = True

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
    
