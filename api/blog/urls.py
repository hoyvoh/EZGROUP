from django.urls import path
from . import views


urlpatterns = [
    # Posts
    path('posts/', views.PostListView.as_view(), name='post-list'),  # GET: List all posts
    path('posts/create/', views.PostCreateView.as_view(), name='post-create'),  # POST: Create a post
    path('posts/<int:post_id>/', views.PostDetails.as_view(), name='post-details'),  # GET: Post details
    path('posts/<int:post_id>/update/', views.PostUpdateView.as_view(), name='post-update'),  # PUT/PATCH: Update a post
    path('posts/<int:post_id>/delete/', views.PostDeleteView.as_view(), name='post-delete'),  # DELETE: Delete a post

    path('posts/<int:post_id>/likes/', views.LikeListView.as_view(), name='post-like-list'),  # GET: List likes
    path('posts/<int:post_id>/likes/create/', views.LikeCreateView.as_view(), name='post-like-create'),  # POST: Like a post
    path('posts/<int:post_id>/likes/<int:like_id>/delete/', views.LikeDeleteView.as_view(), name='post-like-delete'),  # DELETE: Unlike

    # Images
    path('posts/<int:post_id>/images/', views.ImageListView.as_view(), name='post-image-list'),  # GET: List images
    path('posts/<int:post_id>/images/upload/', views.ImageCreateView.as_view(), name='post-image-create'),  # POST: Upload image
    # Comments
    path('posts/<int:post_id>/comments/', views.CommentListView.as_view(), name='post-comment-list'),  # GET: List comments
    path('posts/<int:post_id>/comments/create/', views.CommentCreateView.as_view(), name='post-comment-create'),  # POST: Create comment
    path('posts/<int:post_id>/comments/<int:comment_id>/update/', views.CommentUpdateView.as_view(), name='post-comment-update'),  # PUT/PATCH: Update comment
    path('posts/<int:post_id>/comments/<int:comment_id>/delete/', views.CommentDeleteView.as_view(), name='post-comment-delete'),  # DELETE: Delete comment
]
