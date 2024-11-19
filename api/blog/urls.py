# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views


urlpatterns = [
    path('posts/', views.PostListCreateView.as_view(), name='post-list-create'),
    path('posts/<int:pk>/', views.PostDetailUpdateDeleteView.as_view(), name='post-detail-update-delete'),
    path('posts/<int:pk>/like/', views.LikePostView.as_view(), name='like-post'),
    path('posts/<int:pk>/share/', views.SharePostView.as_view(), name='share-post'),
    path('posts/<int:pk>/images/', views.ImageListCreateView.as_view(), name='image-list-create'),
    path('posts/<int:post_id>/comments/', views.CommentListCreateView.as_view(), name='comment-list-create'),
    path('posts/<int:post_id>/comment/<int:comment_id>/', views.CommentUpdateDeleteView.as_view(), name='comment-delete-update'),
    path('notifications/', views.NotificationListView.as_view(), name='notification-list'),
    path('notifications/<int:id>/mark-read/', views.MarkNotificationAsReadView.as_view(), name='notification-mark-read'),
]
