from django.contrib import admin
from django.urls import path, include
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework.permissions import AllowAny

schema_view = get_schema_view(
    openapi.Info(
        title="EZGroup Web API",
        default_version='v1',
        description='''This API allows users to interact with a blogging platform, providing functionalities such as creating, viewing, updating, and deleting blog posts, managing user sessions, posting comments, and handling likes and shares. The API includes endpoints for managing posts, user sessions, notifications, and media such as images. The documentation provides detailed specifications of each endpoint, request parameters, and responses, enabling users to easily explore and test the API.

                        You can adjust or expand this description based on the specific features and endpoints your API supports.''',
        terms_of_service="https://www.yourterms.com/",
        contact=openapi.Contact(email="ezgroup.help@gmail.com"),
        license=openapi.License(name="MIT"),
    ),
    public=True,
    permission_classes=[AllowAny],  # Use the appropriate permission class for your API
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/authen/', include('authen.urls')),
    path('api/v1/blog/', include('blog.urls')),
    path('api/v1/subscribe/', include('subscribe.urls')),
    path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]
