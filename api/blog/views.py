from rest_framework import permissions, status, views
from .models import Post, Image, Like, Notification, Comment, UserSession
from .serializers import PostSerializer, ImageSerializer, LikeSerializer, ShareSerializer, CommentSerializer, NotificationSerializer, UserSessionSerializer
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user.is_superuser:
            return True
        return obj.author == request.user

class UserSessionCreateView(views.APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_summary="Create a User Session",
        request_body=UserSessionSerializer,
        manual_parameters=[
            openapi.Parameter(
                'Authorization',
                openapi.IN_HEADER,
                description="Bearer token to identify the user creating the session",
                type=openapi.TYPE_STRING,
                required=True,
            )
        ],
        responses={
            201: "User session created successfully",
            400: "Invalid input data",
            401: "Authentication failed",
        }
    )
    def post(self, request, *args, **kwargs):
        auth_header = request.headers.get('Authorization', None)
        if not auth_header:
            return Response(
                {"error": "Authorization header is missing."},
                status=status.HTTP_400_BAD_REQUEST
            )
        token = auth_header.split(' ')[-1] 
        session_data = {'session_token': token, 'is_anonymous': False}
        serializer = UserSessionSerializer(data=session_data)
        
        if serializer.is_valid():
            session = serializer.save()  
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PostCreateView(views.APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_summary="Create a post",
        request_body=PostSerializer,
        manual_parameters=[
            openapi.Parameter(
                'Session-Token',
                openapi.IN_HEADER,
                description="Session token for the user accessing the post",
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
        session_token = request.headers.get('Session-Token')

        try:
            author_session = UserSession.objects.get(session_token=session_token)
        except UserSession.DoesNotExist:
            return Response(
                {"error": "Invalid or missing session token."},
                status=status.HTTP_400_BAD_REQUEST
            )

        data['author_session'] = author_session.id
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
        posts = Post.objects.all().select_related('author_session').prefetch_related('images')
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
                'Session-Token',
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
                'Session-Token',
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
                'Session-Token',
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
    
    
class LikePostView(views.APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_summary="Like a post",
        request_body=LikeSerializer,  
        manual_parameters=[ 
            openapi.Parameter(
                'Session-Token',
                openapi.IN_HEADER,
                description="Session token for the user accessing the post",
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
    def post(self, request, pk):
        post = Post.objects.filter(pk=pk).first()
        if not post:
            return Response({"detail": "Post not found"}, status=status.HTTP_404_NOT_FOUND)
        if Like.objects.filter(user=request.user, post=post).exists():
            return Response({"detail": "You have already liked this post."}, status=status.HTTP_400_BAD_REQUEST)
        like = Like.objects.create(user=request.user, post=post)
        serializer = LikeSerializer(like)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        operation_summary="Unlike a post",
        manual_parameters=[ 
            openapi.Parameter(
                'Session-Token',
                openapi.IN_HEADER,
                description="Session token for the user accessing the post",
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
    def delete(self, request, pk):
        post = Post.objects.filter(pk=pk).first()
        if not post:
            return Response({"detail": "Post not found"}, status=status.HTTP_404_NOT_FOUND)
        like = Like.objects.filter(user=request.user, post=post).first()
        if not like:
            return Response({"detail": "You haven't liked this post."}, status=status.HTTP_400_BAD_REQUEST)
        like.delete()
        return Response({"detail": "Like removed successfully"}, status=status.HTTP_204_NO_CONTENT)



class SharePostView(views.APIView):
    permission_classes = [permissions.AllowAny]

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
                'Session-Token',
                openapi.IN_HEADER,
                description="Session token for the user accessing the comments",
                type=openapi.TYPE_STRING,
                required=True,
            )
        ],
        responses={
            201: "Post liked successfully",
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

        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(post=post, author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
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
                'Session-Token',
                openapi.IN_HEADER,
                description="Session token for the user accessing the comment",
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
    def put(self, request, pk):
        comment = self.get_object(pk)
        if comment.author != request.user:
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
                'Session-Token',
                openapi.IN_HEADER,
                description="Session token for the user accessing the comment",
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
    def delete(self, request, pk):
        comment = self.get_object(pk)
        if comment.author != request.user and not request.user.is_superuser:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        comment.delete()
        return Response({'status': 'Comment deleted'}, status=status.HTTP_204_NO_CONTENT)

class NotificationListView(views.APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_summary="Image List View",
        responses={200: NotificationSerializer(many=True)},
    )
    def get(self, request, *args, **kwargs):
        notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data)

class MarkNotificationAsReadView(views.APIView):
    permission_classes = [permissions.AllowAny]  

    @swagger_auto_schema(
        operation_summary="Mark a notification as read",
        manual_parameters=[
            openapi.Parameter(
                'Session-Token',
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
        try:
            notification = Notification.objects.get(id=notification_id, user=request.user)
            notification.is_read = True
            notification.save()

            return Response({'status': 'Notification marked as read'}, status=status.HTTP_200_OK)
        
        except Notification.DoesNotExist:
            return Response({'error': 'Notification not found'}, status=status.HTTP_404_NOT_FOUND)
    
class NotificationDeleteView(views.APIView):
    permission_classes = [permissions.AllowAny]
    @swagger_auto_schema(
        operation_summary="Delete a notification",
        manual_parameters=[ 
            openapi.Parameter(
                'Session-Token',
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
        try:
            notification = Notification.objects.get(id=pk, user=request.user)
        except Notification.DoesNotExist:
            return Response({'error': 'Notification not found or invalid request'}, status=status.HTTP_404_NOT_FOUND)
        notification.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

