from rest_framework import serializers
from .models import Post, Image, Comment, Like, Share, Notification

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['id', 'post', 'image_url', 'label']

class PostSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author_session.user.get_full_name', read_only=True)
    images = ImageSerializer(many=True, read_only=True)
    likes_count = serializers.IntegerField(source='likes.count', read_only=True)
    shares_count = serializers.IntegerField(source='shares.count', read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'title', 'content', 'category', 'author_name', 'author_email', 'created_at', 'last_modified', 'images', 'likes_count', 'shares_count']
        read_only_fields = ['author_session', 'created_at', 'last_modified']
        

class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ['id', 'user', 'post', 'created_at']
        read_only_fields = ['user', 'created_at']

class ShareSerializer(serializers.ModelSerializer):
    class Meta:
        model = Share
        fields = ['id', 'user', 'post', 'created_at', 'platform']
        read_only_fields = ['user', 'created_at']

class CommentSerializer(serializers.ModelSerializer):
    author_name = serializers.ReadOnlyField(source='author.username')

    class Meta:
        model = Comment
        fields = ['id', 'post', 'author_name', 'content', 'created_at']
        
class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'message', 'is_read', 'created_at']
