from rest_framework import serializers
from .models import Post, Image, Comment, Like 
import boto3
from django.conf import settings

class ImageSerializer(serializers.ModelSerializer):
    file = serializers.ImageField(write_only=True, required=True)
    class Meta:
        model = Image
        fields = ['id', 'post', 'label', 'image_url', 'file']
        read_only_fields = ['image_url']
    
    def create(self, validated_data):
        file = validated_data.pop('file')
        post = validated_data.get('post')
        
        s3_client = boto3.client('s3',
                                 aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                                 aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,)

        folder = f'{post.id}'
        
        file_key = f"{settings.PUBLIC_MEDIA_LOCATION}/{folder}/{file.name}"
        
        s3_client.upload_fileobj(file, settings.AWS_STORAGE_BUCKET_NAME, file_key)

        image_url = f"https://{settings.AWS_S3_CUSTOM_DOMAIN}/{file_key}"

        image = Image.objects.create(
            post=post,
            label=validated_data.get('label', ''),
            image_url=image_url
        )
        return image

class PostSerializer(serializers.ModelSerializer):
    likes_count = serializers.IntegerField(source='likes.count', read_only=True)
    shares_count = serializers.IntegerField(source='shares.count', read_only=True)
    comments_count = serializers.IntegerField(source='comments.count', read_only=True)
    class Meta:
        model = Post
        fields = [
            'id', 'title', 'content', 'category', 'user_id', 
            'user_name', 'user_email','created_at',
            'likes_count', 'shares_count', 'comments_count'
        ]
        read_only_fields = ['created_at', 'last_modified']

class CommentSerializer(serializers.ModelSerializer):
    parent = serializers.PrimaryKeyRelatedField(
        queryset=Comment.objects.all(),
        required=False,
        allow_null=True 
    ) 
    commenter_name = serializers.CharField(source='user_name', read_only=True)  
    replies_count = serializers.IntegerField(source='replies.count', read_only=True) 
    class Meta:
        model = Comment
        fields = [
            'id', 'content', 'created_at', 'user_id', 'user_name', 
            'user_email', 'parent', 'commenter_name', 'replies_count',
        ]
        read_only_fields = ['created_at', 'user_id', 'user_name', 'user_email']

class LikeSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(read_only=True)
    class Meta:
        model = Like
        fields = ['user_id', 'user_name', 'user_email', 'created_at']
        read_only_fields = ['created_at']
 

