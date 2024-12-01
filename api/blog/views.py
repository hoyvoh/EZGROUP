from rest_framework import permissions, status, views
from .models import Post, Image, Like, Comment
from .serializers import PostSerializer, ImageSerializer, LikeSerializer, CommentSerializer
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from drf_yasg import openapi
import requests
import os
from dotenv import load_dotenv
load_dotenv()

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
            201: PostSerializer,
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
            
            try:
                sending_data = data
                sending_data['created_at'] = post.created_at.isoformat()
                sending_data['id'] = post.id
                if len(images_data) >0:
                    sending_data['first_image'] = Image.objects.filter(post_id=post.id).first().image_url
                else:
                    sending_data['first_image'] ='https://ezgroup-static-files-bucket.s3.ap-southeast-2.amazonaws.com/media/ezgroup-logo.jpg'
                print(sending_data)
                fastapi_url = f"{os.getenv("NEWSLETTER_ENDPOINT")}/posts/"
                response = requests.post(fastapi_url, json=sending_data)

                if response.status_code == 200:
                    return Response({
                        "EC": 1,
                        "EM": "Success",
                        "DT": serializer.data
                    }, status=status.HTTP_200_OK)
                else:
                    return Response({
                        "EC": 1,
                        "EM": f"Failed to add post to newsletter. Yet, saved post. Error: {response.text}",
                        "DT": serializer.data
                    }, status=status.HTTP_201_CREATED)

            except requests.exceptions.RequestException as e:
                return Response({
                    "EC": 0,
                    "EM": f"Error while sending post to FastAPI server: {e}"
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PostListView(views.APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_summary="List all posts",
        responses={200: PostSerializer(many=True)},
    )
    def get(self, request):
        posts = Post.objects.all().prefetch_related('likes',  'comments')
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PostDetails(views.APIView):
    permission_classes = [permissions.AllowAny]

    def get_object(self, post_id):
        return get_object_or_404(Post, pk=post_id)

    @swagger_auto_schema(
        operation_summary="Post Details",
        responses={
            200: PostSerializer,
            404: "Post not found"
        },
    )
    def get(self, request, post_id):
        post = self.get_object(post_id)

        serializer = PostSerializer(post)
        return Response({
            "EC": 1,
            "EM": "Success",
            "DT": serializer.data
        }, status=status.HTTP_200_OK)

class PostUpdateView(views.APIView):
    permission_classes = [permissions.AllowAny] 

    def get_object(self, post_id):
        return get_object_or_404(Post, pk=post_id)

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
    def put(self, request, post_id):
        post = self.get_object(post_id)
        user_data = getattr(request, 'user_data', None) 
        print(user_data)
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

    
    
class PostDeleteView(views.APIView):
    permission_classes = [permissions.AllowAny] 

    def get_object(self, post_id):
        return get_object_or_404(Post, pk=post_id)
    
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
    def delete(self, request, post_id):
        post = self.get_object(post_id)
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

from rest_framework.parsers import MultiPartParser, FormParser

class ImageCreateView(views.APIView):
    permission_classes = [permissions.AllowAny]  
    parser_classes = [MultiPartParser, FormParser]  

    @swagger_auto_schema(
        operation_summary="Create an image for a post",
        manual_parameters=[
            openapi.Parameter(
                'Authorization',
                openapi.IN_HEADER,
                description="Session token for the user accessing the image",
                type=openapi.TYPE_STRING,
                required=True,
            )
        ],
        request_body=ImageSerializer,
        responses={
            201: "Image uploaded successfully",
            400: "Invalid input",
            401: "Authentication failed",
            403: "Permission denied",
        }
    )
    def post(self, request, post_id, *args, **kwargs):
        try:
            try:
                post = Post.objects.get(pk=post_id)
            except Post.DoesNotExist:
                return Response(
                    {"EC": -1, "EM": "Post not found", "DT": ""},
                    status=status.HTTP_404_NOT_FOUND,
                )

            request_data = request.data.copy()
            request_data["post"] = post.id

            serializer = ImageSerializer(data=request_data)
            if not serializer.is_valid():
                return Response(
                    {"EC": -1, "EM": "Invalid input", "DT": serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            
            image = serializer.save()
            return Response(
                {"EC": 1, "EM": "Image saved successfully", "DT": serializer.data},
                status=status.HTTP_201_CREATED,
            )

        except Exception as e:
            return Response(
                {"EC": -1, "EM": f"Error saving image: {str(e)}", "DT": ""},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        
class ImageUpdateView(views.APIView):
    permission_classes = [permissions.AllowAny]
    parser_classes = [MultiPartParser, FormParser]

    @swagger_auto_schema(
        operation_summary="Update an image for a post",
        manual_parameters=[
            openapi.Parameter(
                'Authorization',
                openapi.IN_HEADER,
                description="Session token for the user accessing the image",
                type=openapi.TYPE_STRING,
                required=True,
            )
        ],
        request_body=ImageSerializer,
        responses={
            200: "Image updated successfully",
            400: "Invalid input",
            401: "Authentication failed",
            403: "Permission denied",
        },
    )
    def put(self, request, post_id, image_id, *args, **kwargs):
        try:
            try:
                post = Post.objects.get(pk=post_id)
            except Post.DoesNotExist:
                return Response(
                    {"EC": -1, "EM": "Post not found", "DT": ""},
                    status=status.HTTP_404_NOT_FOUND,
                )

            try:
                image = Image.objects.get(pk=image_id, post=post)
            except Image.DoesNotExist:
                return Response(
                    {"EC": -1, "EM": "Image not found for this post", "DT": ""},
                    status=status.HTTP_404_NOT_FOUND,
                )

            if post.user != request.user:
                return Response(
                    {"EC": -1, "EM": "Permission denied", "DT": ""},
                    status=status.HTTP_403_FORBIDDEN,
                )

            serializer = ImageSerializer(image, data=request.data, partial=True)
            if not serializer.is_valid():
                return Response(
                    {"EC": -1, "EM": "Invalid input", "DT": serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            serializer.save()
            return Response(
                {"EC": 1, "EM": "Image updated successfully", "DT": serializer.data},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"EC": -1, "EM": f"Error updating image: {str(e)}", "DT": ""},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ImageDeleteView(views.APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_summary="Delete an image for a post",
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
            200: "Image deleted successfully",
            404: "Image not found",
            401: "Authentication failed",
            403: "Permission denied",
        },
    )
    def delete(self, request, post_id, image_id, *args, **kwargs):
        try:
            try:
                post = Post.objects.get(pk=post_id)
            except Post.DoesNotExist:
                return Response(
                    {"EC": -1, "EM": "Post not found", "DT": ""},
                    status=status.HTTP_404_NOT_FOUND,
                )

            try:
                image = Image.objects.get(pk=image_id, post=post)
            except Image.DoesNotExist:
                return Response(
                    {"EC": -1, "EM": "Image not found for this post", "DT": ""},
                    status=status.HTTP_404_NOT_FOUND,
                )

            if post.user != request.user:
                return Response(
                    {"EC": -1, "EM": "Permission denied", "DT": ""},
                    status=status.HTTP_403_FORBIDDEN,
                )

            image.delete()
            return Response(
                {"EC": 1, "EM": "Image deleted successfully", "DT": ""},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"EC": -1, "EM": f"Error deleting image: {str(e)}", "DT": ""},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

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
        post = get_object_or_404(Post, pk=post_id)

        # Initialize user data
        user_data = getattr(request, 'user_data', None)
        data = request.data.copy()  # Copy data to avoid mutating request.data

        # Set user information if authenticated
        if user_data:
            data['user_id'] = user_data.get('id')
            data['user_name'] = user_data.get('full_name')
            data['user_email'] = user_data.get('email')
        else:
            return Response({"error": "Permission denied. You cannot delete another user's post."},
                             status=status.HTTP_403_FORBIDDEN)
            # data['user_id'] = 'anonymous'
            # data['user_name'] = 'Anonymous'
            # data['user_email'] = 'anonymous@gmail.com'

        parent_id = data.get('parent')
        if parent_id is not None and parent_id != '':
            if not Comment.objects.filter(id=parent_id).exists():
                return Response({'error': f"Parent comment with ID {parent_id} does not exist."}, 
                                status=status.HTTP_400_BAD_REQUEST)

        print('check data comment create:', data)
        serializer = CommentSerializer(data=data)

        if serializer.is_valid():
            comment = serializer.save(post=post)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class CommentUpdateView(views.APIView):
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

class CommentDeleteView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def get_object(self, post_id, comment_id):
        try:
            post = Post.objects.get(id=post_id)
            comment = Comment.objects.get(id=comment_id, post=post)
            return comment
        except (Post.DoesNotExist, Comment.DoesNotExist):
            return None
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

class LikeCreateView(views.APIView):
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
                required=False, 
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
        
        if user_data:
            user_id = user_data.get('id')
            user_name = user_data.get('full_name')
            user_email = user_data.get('email')
        else:
            return Response({"error": "Permission denied. You cannot delete another user's post."},
                             status=status.HTTP_403_FORBIDDEN)

        if Like.objects.filter(user_id=user_id, post=post).exists() and user_id != 'anonymous':
            return Response({"detail": "You have already liked this post."}, status=status.HTTP_400_BAD_REQUEST)

        like_instance = Like(
            user_id=user_id,
            user_name=user_name,
            user_email=user_email,
            post=post
        )

        like_instance.save()

        serializer = LikeSerializer(like_instance)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class LikeDeleteView(views.APIView):
    permission_classes = [permissions.AllowAny]
    @swagger_auto_schema(
        operation_summary="Unlike a post",
        manual_parameters=[
            openapi.Parameter(
                'Authorization',
                openapi.IN_HEADER,
                description="Session token for the user unliking the post",
                type=openapi.TYPE_STRING,
                required=False, 
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
        if user_data:
            user_id = user_data.get('id')
        else:
            return Response({"error": "Authentication failed"}, status=status.HTTP_401_UNAUTHORIZED)
        if user_id != 'anonymous':
            like = Like.objects.filter(user_id=user_id, post=post).first()
            if not like:
                return Response({"detail": "You haven't liked this post."}, status=status.HTTP_400_BAD_REQUEST)

        like.delete()
        return Response({"detail": "Unlike successfully"}, status=status.HTTP_204_NO_CONTENT)

class LikeListView(views.APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_summary="List all likes for a post",
        manual_parameters=[
            openapi.Parameter(
                'Authorization',
                openapi.IN_HEADER,
                description="Session token for the user",
                type=openapi.TYPE_STRING,
                required=False,
            )
        ],
        responses={
            200: "List of likes",
            404: "Post not found",
        },
    )
    def get(self, request, post_id):
        post = Post.objects.filter(pk=post_id).first()
        if not post:
            return Response({"detail": "Post not found"}, status=status.HTTP_404_NOT_FOUND)

        likes = Like.objects.filter(post=post)
        serializer = LikeSerializer(likes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
