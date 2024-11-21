from rest_framework import permissions, status, views
from .models import Post, Image, Like, Notification, Comment
from .serializers import PostSerializer, ImageSerializer, LikeSerializer, CommentSerializer, NotificationSerializer
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from drf_yasg import openapi


class PostCreateView(views.APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_summary="Create a post",
        request_body=PostSerializer,
        manual_parameters=[ 
            openapi.Parameter(
                'Authorization',
                openapi.IN_HEADER,
                description="Bearer token for the user accessing the post",
                type=openapi.TYPE_STRING,
                required=True,
            )
        ],
        responses={  
            201: "Post Created",
            400: "Invalid input",
            401: "Authentication failed",
            403: "Permission denied",
        },
    )
    def post(self, request, *args, **kwargs):
        data = request.data
        user_data = getattr(request, 'user_data', None)
        if user_data:
            data['user_id'] = user_data.get('id')
            data['user_name'] = user_data.get('full_name')
            data['user_email'] = user_data.get('email')

        serializer = PostSerializer(data=data)
        if serializer.is_valid():
            post = serializer.save()
            images_data = data.get('images', [])
            for image_data in images_data:
                Image.objects.create(post=post, **image_data)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PostListView(views.APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_summary="List all posts",
        responses={200: PostSerializer(many=True)},
    )
    def get(self, request, *args, **kwargs):
        posts = Post.objects.all().select_related('user').prefetch_related('likes', 'shares', 'comments')
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PostDetails(views.APIView):
    permission_classes = [permissions.AllowAny]

    def get_object(self, pk):
        return get_object_or_404(Comment, pk=pk)

    @swagger_auto_schema(
        operation_summary="Post Details",
        responses={200: PostSerializer(many=True)},
    )
    def get(self, request, pk):
        post = self.get_object(pk)
        if post is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

class PostUpdateDeleteView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def get_object(self, pk):
        return get_object_or_404(Post, pk=pk)

    def get(self, request, pk):
        post = self.get_object(pk)
        serializer = PostSerializer(post)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="Modify a post",
        request_body=PostSerializer,
        manual_parameters=[
            openapi.Parameter(
                'Authorization',
                openapi.IN_HEADER,
                description="Session token for the user accessing the post",
                type=openapi.TYPE_STRING,
                required=True,
            )
        ],
        responses={
            200: PostSerializer,  
            400: "Invalid input",
            401: "Authentication failed",
            403: "Permission denied",
        },
    )
    def put(self, request, pk):
        post = self.get_object(pk)
        user_data = getattr(request, 'user_data', None)
        if not user_data:
            return Response({"error": "User not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)
        if post.user_id != user_data.get('id'):
            return Response({"error": "Permission denied. You cannot modify another user's post."}, 
                            status=status.HTTP_403_FORBIDDEN)
        self.check_object_permissions(request, post)
        serializer = PostSerializer(post, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_summary="Delete a post",
        manual_parameters=[
            openapi.Parameter(
                'Authorization',
                openapi.IN_HEADER,
                description="Session token for the user accessing the post",
                type=openapi.TYPE_STRING,
                required=True,
            )
        ],
        responses={
            204: "No Content",  
            401: "Authentication failed",
            403: "Permission denied",
        },
    )
    def delete(self, request, pk):
        post = self.get_object(pk)
        user_data = getattr(request, 'user_data', None)
        if not user_data:
            return Response({"error": "User not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)
        if post.user_id != user_data.get('id'):
            return Response({"error": "Permission denied. You cannot delete another user's post."}, 
                            status=status.HTTP_403_FORBIDDEN)
        self.check_object_permissions(request, post)
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

class ImageListView(views.APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_summary="Image List View",
        responses={200: ImageSerializer(many=True)},
    )
    def get(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        images = post.images.all()
        serializer = ImageSerializer(images, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class ImageCreateView(views.APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_summary="Create a post",
        request_body=ImageSerializer,
        manual_parameters=[
            openapi.Parameter(
                'Authorization',
                openapi.IN_HEADER,
                description="Session token for the user accessing the image",
                type=openapi.TYPE_STRING,
                required=True,
            )
        ],
        responses={
            201: "Image uploaded successfully",
            400: "Invalid input",
            401: "Authentication failed",
            403: "Permission denied",
        },
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

class CommentListView(views.APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_summary="Image List View",
        responses={200: CommentSerializer(many=True)},
    )
    def get(self, request, post_id):
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)

        comments = Comment.objects.filter(post=post)
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

class CommentCreateView(views.APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_summary="Comment on a post",
        request_body=CommentSerializer,
        manual_parameters=[
            openapi.Parameter(
                'Authorization',
                openapi.IN_HEADER,
                description="Bearer token for the user accessing the comments",
                type=openapi.TYPE_STRING,
                required=True,
            )
        ],
        responses={
            201: "Comment created successfully",
            400: "Invalid input",
            401: "Authentication failed",
            403: "Permission denied",
        },
    )
    def post(self, request, post_id):
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)

        user_data = getattr(request, 'user_data', None)
        data = request.data
        if user_data:
            data['user_id'] = user_data.get('id')
            data['user_name'] = user_data.get('full_name')
            data['user_email'] = user_data.get('email')

        serializer = CommentSerializer(data=data)
        if serializer.is_valid():
            comment = serializer.save(post=post)  

            self.create_notification(
                recipient_id=post.user_id,  
                recipient_name=post.user_name,
                recipient_email=post.user_email,
                message=f"Your post '{post.title}' has a new comment by {data['user_name']}: '{comment.content}'"
            )  
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def create_notification(self, recipient_id, recipient_name, recipient_email, message):
        Notification.objects.create(
            user_id=recipient_id,
            user_name=recipient_name,
            user_email=recipient_email,
            message=message,
        )
        
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"user_{recipient_id}", 
            {
                "type": "send_notification",
                "message": message,
            }
        )
    
class CommentUpdateDeleteView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def get_object(self, post_id, comment_id):
        try:
            post = Post.objects.get(id=post_id)
            comment = Comment.objects.get(id=comment_id, post=post)
            return comment
        except (Post.DoesNotExist, Comment.DoesNotExist):
            return None

    @swagger_auto_schema(
        operation_summary="Modify a comment",
        request_body=CommentSerializer,
        manual_parameters=[
            openapi.Parameter(
                'Authorization',
                openapi.IN_HEADER,
                description="Bearer token for the user accessing the comment",
                type=openapi.TYPE_STRING,
                required=True,
            )
        ],
        responses={
            200: "Comment Edited",  
            400: "Invalid input",
            401: "Authentication failed",
            403: "Permission denied",
        },
    )
    def put(self, request, post_id, comment_id):
        comment = self.get_object(post_id, comment_id)
        if not comment:
            return Response({'error': 'Comment or post not found'}, status=status.HTTP_404_NOT_FOUND)

        user_data = getattr(request, 'user_data', None)
        if not user_data or comment.user_id != user_data.get('id'):
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        serializer = CommentSerializer(comment, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_summary="Delete a comment",
        manual_parameters=[ 
            openapi.Parameter(
                'Authorization',
                openapi.IN_HEADER,
                description="Bearer token for the user accessing the comment",
                type=openapi.TYPE_STRING,
                required=True,
            )
        ],
        responses={ 
            204: "No Content",
            400: "Invalid request",
            401: "Authentication failed",
            403: "Permission denied",
        },
    )
    def delete(self, request, post_id, comment_id):
        comment = self.get_object(post_id, comment_id)
        if not comment:
            return Response({'error': 'Comment or post not found'}, status=status.HTTP_404_NOT_FOUND)

        user_data = getattr(request, 'user_data', None)
        if not user_data or (comment.user_id != user_data.get('id') and not request.user.is_superuser):
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        comment.delete()
        return Response({'status': 'Comment deleted'}, status=status.HTTP_204_NO_CONTENT)

class LikeCreateDeleteView(views.APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_summary="Like a post",
        request_body=LikeSerializer,
        manual_parameters=[ 
            openapi.Parameter(
                'Authorization',
                openapi.IN_HEADER,
                description="Session token for the user liking the post",
                type=openapi.TYPE_STRING,
                required=True,
            )
        ],
        responses={  
            201: "Liked post",
            400: "Invalid input (already liked)",
            401: "Authentication failed",
            403: "Permission denied",
        },
    )
    def post(self, request, post_id):
        post = Post.objects.filter(pk=post_id).first()
        if not post:
            return Response({"detail": "Post not found"}, status=status.HTTP_404_NOT_FOUND)
        user_data = getattr(request, 'user_data', None)
        if not user_data:
            return Response({"error": "Authentication failed"}, status=status.HTTP_401_UNAUTHORIZED)
        if Like.objects.filter(user_id=user_data.get('id'), post=post).exists():
            return Response({"detail": "You have already liked this post."}, status=status.HTTP_400_BAD_REQUEST)
        data = request.data
        data['user_id'] = user_data.get('id')
        data['user_name'] = user_data.get('full_name')
        data['user_email'] = user_data.get('email')

        serializer = LikeSerializer(data=data)
        if serializer.is_valid():
            serializer.save(post=post)
            self.create_notification(
                recipient_id=post.user_id,  
                recipient_name=post.user_name,
                recipient_email=post.user_email,
                message=f"Your post '{post.title}' was liked by {data['user_name']}."
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_summary="Unlike a post",
        manual_parameters=[ 
            openapi.Parameter(
                'Authorization',
                openapi.IN_HEADER,
                description="Session token for the user unliking the post",
                type=openapi.TYPE_STRING,
                required=True,
            )
        ],
        responses={ 
            204: "No Content",
            400: "You haven't liked this post",
            401: "Authentication failed",
            403: "Permission denied",
        },
    )
    def delete(self, request, post_id):
        post = Post.objects.filter(pk=post_id).first()
        if not post:
            return Response({"detail": "Post not found"}, status=status.HTTP_404_NOT_FOUND)
        user_data = getattr(request, 'user_data', None)
        if not user_data:
            return Response({"error": "Authentication failed"}, status=status.HTTP_401_UNAUTHORIZED)

        like = Like.objects.filter(user_id=user_data.get('id'), post=post).first()
        if not like:
            return Response({"detail": "You haven't liked this post."}, status=status.HTTP_400_BAD_REQUEST)

        like.delete()
        return Response({"detail": "Like removed successfully"}, status=status.HTTP_204_NO_CONTENT)

    def create_notification(self, recipient_id, recipient_name, recipient_email, message):
        Notification.objects.create(
            user_id=recipient_id,
            user_name=recipient_name,
            user_email=recipient_email,
            message=message,
        )
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"user_{recipient_id}", 
            {
                "type": "send_notification",
                "message": message,
            }
        )

class NotificationListView(views.APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_summary="Get Notifications for a User",
        responses={200: NotificationSerializer(many=True)},
    )
    def get(self, request):
        user_id = getattr(request, 'user_data', {}).get('id') 
        if not user_id:
            return Response({"error": "User not authenticated"}, status=status.HTTP_400_BAD_REQUEST)
        notifications = Notification.objects.filter(user_id=user_id).order_by('-created_at')
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data)


class MarkNotificationAsReadView(views.APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_summary="Mark a notification as read",
        manual_parameters=[  
            openapi.Parameter(
                'Authorization',
                openapi.IN_HEADER,
                description="Session token for the user accessing the notifications",
                type=openapi.TYPE_STRING,
                required=True,
            )
        ],
        responses={
            200: "Notification marked as read successfully",
            400: "Invalid input",
            401: "Authentication failed",
            403: "Permission denied",
            404: "Notification not found",
        },
    )
    def post(self, request, notification_id, *args, **kwargs):
        user_data = getattr(request, 'user_data', None)
        if not user_data:
            return Response({"error": "User not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            notification = Notification.objects.get(id=notification_id, user_id=user_data.get('id'))
            notification.is_read = True 
            notification.save()
            return Response({'status': 'Notification marked as read'}, status=status.HTTP_200_OK)
        
        except Notification.DoesNotExist:
            return Response({'error': 'Notification not found or you do not have permission to mark it'}, status=status.HTTP_404_NOT_FOUND)

    
class NotificationDeleteView(views.APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_summary="Delete a notification",
        manual_parameters=[
            openapi.Parameter(
                'Authorization',
                openapi.IN_HEADER,
                description="Session token for the user accessing the notification",
                type=openapi.TYPE_STRING,
                required=True,
            )
        ],
        responses={
            204: "No Content",
            400: "Notification not found or invalid request",
            401: "Authentication failed",
            403: "Permission denied",
        },
    )
    def delete(self, request, pk):
        user_data = getattr(request, 'user_data', None)
        if not user_data:
            return Response({"error": "User not authenticated or user_data missing"}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            notification = Notification.objects.get(id=pk, user_id=user_data.get('id'))
            notification.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Notification.DoesNotExist:
            return Response({'error': 'Notification not found or you do not have permission to delete it'}, status=status.HTTP_404_NOT_FOUND)


