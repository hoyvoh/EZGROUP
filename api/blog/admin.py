from django.contrib import admin
from .models import Post, Like, Image, Comment, Notification

# Register your models here.
admin.site.register(Post)
admin.site.register(Like)
admin.site.register(Image)
admin.site.register(Comment)
admin.site.register(Notification)
