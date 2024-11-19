from rest_framework import permissions, status, views
from .models import Post, Image, Like, Notification, Comment
from .serializers import PostSerializer, ImageSerializer, LikeSerializer, ShareSerializer, CommentSerializer, NotificationSerializer
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema


class IsStaffOrReadOnly(permissions.BasePermission):
    """Allow read-only access to any user but restrict write access to staff users only."""
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.is_staff

class IsAuthenticatedOrReadOnly(permissions.BasePermission):
    """Allow read-only access to any user but restrict write access to authenticated users only."""
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated


class PostListCreateView(views.APIView):
    permission_classes = [IsStaffOrReadOnly]

    @swagger_auto_schema(
        request_body=PostSerializer,  
        responses={201: PostSerializer, 400: 'Bad Request'}
    )
    def post(self, request):
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        posts = Post.objects.all()
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)



class PostDetailUpdateDeleteView(views.APIView):
    permission_classes = [IsStaffOrReadOnly]

    def get_object(self, pk):
        return get_object_or_404(Comment, pk=pk)

    def get(self, request, pk):
        post = self.get_object(pk)
        if post is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = PostSerializer(post)
        return Response(serializer.data)

    @swagger_auto_schema(
        request_body=PostSerializer, 
        responses={200: PostSerializer, 400: 'Bad Request'}
    )
    def put(self, request, pk):
        post = self.get_object(pk)
        if post is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = PostSerializer(post, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        post = self.get_object(pk)
        if post is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

class ImageListCreateView(views.APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, post_id):
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)

        images = Image.objects.filter(post=post)
        serializer = ImageSerializer(images, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        request_body=ImageSerializer,
        responses={201: ImageSerializer, 400: 'Bad Request'}
    )
    def post(self, request, post_id):
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = ImageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(post=post)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class LikePostView(views.APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    @swagger_auto_schema(
        request_body=LikeSerializer, 
        responses={200: LikeSerializer, 400: 'Bad Request'}
    )
    def post(self, request, pk):
        try:
            post = Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if Like.objects.filter(user=request.user, post=post).exists():
            return Response({"detail": "You have already liked this post."}, status=status.HTTP_400_BAD_REQUEST)
        like = Like.objects.create(user=request.user, post=post)
        serializer = LikeSerializer(like)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

class SharePostView(views.APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    @swagger_auto_schema(
        request_body=ShareSerializer, 
        responses={200: ShareSerializer, 400: 'Bad Request'}
    )
    def post(self, request, pk):
        try:
            post = Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = ShareSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, post=post)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CommentListCreateView(views.APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, post_id):
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)

        comments = Comment.objects.filter(post=post)
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        request_body=CommentSerializer, 
        responses={200: CommentSerializer, 400: 'Bad Request'}
    )
    def post(self, request, post_id):
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(post=post, author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class CommentUpdateDeleteView(views.APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    def get_object(self, post_id, comment_id):
        try:
            post = Post.objects.get(id=post_id)
            comment = Comment.objects.get(id=comment_id, post=post)
            return comment
        except (Post.DoesNotExist, Comment.DoesNotExist):
            return None


    @swagger_auto_schema(
        request_body=CommentSerializer,
        responses={200: CommentSerializer, 400: 'Bad Request'}
    )
    def put(self, request, pk):
        comment = self.get_object(pk)

        # Check if the request user is the author of the comment
        if comment.author != request.user:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        serializer = CommentSerializer(comment, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        comment = self.get_object(pk)

        # Check if the request user is the author or has special permissions
        if comment.author != request.user and not request.user.is_staff:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        comment.delete()
        return Response({'status': 'Comment deleted'}, status=status.HTTP_204_NO_CONTENT)

class NotificationListView(views.APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request, *args, **kwargs):
        notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data)

class MarkNotificationAsReadView(views.APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly] 

    @swagger_auto_schema(
        request_body=NotificationSerializer, 
        responses={200: NotificationSerializer, 400: 'Bad Request'}
    )
    def post(self, request, notification_id, *args, **kwargs):
        try:
            notification = Notification.objects.get(id=notification_id, user=request.user)
            notification.is_read = True
            notification.save()
            return Response({'status': 'Notification marked as read'})
        except Notification.DoesNotExist:
            return Response({'error': 'Notification not found'}, status=404)
    
class NotificationDeleteView(views.APIView):
    permission_classes=[IsAuthenticatedOrReadOnly]
    def delete(self, request, pk):
        notification = self.get_object(pk)
        if notification is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        notification.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

