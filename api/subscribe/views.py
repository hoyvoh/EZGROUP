from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from django.core.mail import send_mail
from django.conf import settings
from .models import Subscription
from .serializers import SubscriptionSerializer
from django.template.loader import render_to_string
from drf_yasg.utils import swagger_auto_schema
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os


def send_welcome_email(user_email):
    subject = "Welcome to Our Service"
    message = render_to_string("greetings.html", {"user_email": user_email})
    email = MIMEMultipart()
    email['Subject'] = subject
    email['From'] = settings.DEFAULT_FROM_EMAIL
    email['To'] = user_email
    email.attach(MIMEText(message, "html"))
    
    send_mail(
        subject=subject,
        message='', 
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user_email],
        html_message=message,
        fail_silently=False,
    )

class SubscribeView(APIView):
    permission_classes = [AllowAny]
    serializer_class = SubscriptionSerializer

    @swagger_auto_schema(
        request_body=SubscriptionSerializer, 
        responses={200: SubscriptionSerializer, 400: 'Bad Request'}
    )
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        
        if serializer.is_valid():
            email = serializer.validated_data.get('sub_email')
            if Subscription.objects.filter(sub_email=email).exists():
                return Response(
                    {"message": "You're already subscribed. No duplicate entry was created."},
                    status=status.HTTP_200_OK
                )

            subscription = serializer.save()
            send_welcome_email(user_email=subscription.sub_email)
            return Response(
                {"message": "Subscription successful. A welcome email has been sent."},
                status=status.HTTP_201_CREATED
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


