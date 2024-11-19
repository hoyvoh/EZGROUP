# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views


urlpatterns = [
    path('posts/create-post/', views.PostCreateView.as_view(), name='post-create'),
    path('posts/', views.PostListView.as_view(), name='post-list'),
    path('posts/<int:pk>/', views.PostUpdateDeleteView.as_view(), name='post-update-delete'),
    path('posts/<int:pk>/details/', views.PostDetails.as_view(), name='post-details'),
    path('posts/<int:pk>/like/', views.LikePostView.as_view(), name='like-post'),
    path('posts/<int:pk>/share/', views.SharePostView.as_view(), name='share-post'),
    path('posts/<int:pk>/images/', views.ImageListView.as_view(), name='image-list'),
    path('posts/<int:pk>/images/upload/', views.ImageCreateView.as_view(), name='image-create'),
    path('posts/<int:post_id>/comments/', views.CommentListView.as_view(), name='comment-list'),
    path('posts/<int:post_id>/comments/create/', views.CommentCreateView.as_view(), name='comment-create'),
    path('posts/<int:post_id>/comment/<int:comment_id>/', views.CommentUpdateDeleteView.as_view(), name='comment-delete-update'),
    path('notifications/', views.NotificationListView.as_view(), name='notification-list'),
    path('notifications/<int:id>/delete/', views.NotificationDeleteView.as_view(), name='notification-delete'),
    path('notifications/<int:id>/mark-read/', views.MarkNotificationAsReadView.as_view(), name='notification-mark-read'),
]
