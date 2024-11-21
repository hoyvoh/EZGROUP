from rest_framework import serializers
from .models import Post, Image, Comment, Like, Notification

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['id', 'post', 'image_url', 'label']

class PostSerializer(serializers.ModelSerializer):
    likes_count = serializers.IntegerField(source='likes.count', read_only=True)
    shares_count = serializers.IntegerField(source='shares.count', read_only=True)
    comments_count = serializers.IntegerField(source='comments.count', read_only=True)
    class Meta:
        model = Post
        fields = [
            'id', 'title', 'content', 'category', 'user_id', 
            'user_name', 'user_email',
            'likes_count', 'shares_count', 'comments_count'
        ]
        read_only_fields = ['created_at', 'last_modified']

class CommentSerializer(serializers.ModelSerializer):
    post = PostSerializer(read_only=True) 
    parent = serializers.PrimaryKeyRelatedField(queryset=Comment.objects.all(), required=False)  
    commenter_name = serializers.CharField(source='user_name', read_only=True)  
    replies_count = serializers.IntegerField(source='replies.count', read_only=True) 
    class Meta:
        model = Comment
        fields = [
            'id', 'post', 'content', 'created_at', 'user_id', 'user_name', 
            'user_email', 'parent', 'commenter_name', 'replies_count',
            'user_id', 'user_name', 'user_email',
        ]
        read_only_fields = ['created_at', 'post']

class LikeSerializer(serializers.ModelSerializer):
    post = PostSerializer(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    class Meta:
        model = Like
        fields = ['user_id', 'user_name', 'user_email', 'post', 'created_at']
        read_only_fields = ['created_at', 'post']

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'user_id', 'user_name', 'user_email', 'message', 'is_read', 'created_at']
        read_only_fields = ['user_id', 'user_name', 'user_email', 'created_at']

