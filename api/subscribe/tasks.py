from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from .models import Subscription
from blog.models import Post, Image
from django.conf import settings
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from django.db.models import Prefetch
import logging

logger = logging.getLogger(__name__)

@shared_task
def send_subscription_emails():
    subject = "Weekly Newsletter"
 
    subscribers = Subscription.objects.all()
    posts = Post.objects.all().order_by('-last_modified')[:6].prefetch_related(
    Prefetch('images', queryset=Image.objects.all().order_by('id'), to_attr='first_image')
)

    
    for subscriber in subscribers:
        user_email = subscriber.email
        
        try:
            message = render_to_string("newsletter.html", {"user_email": user_email, "posts": posts})
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
            logger.info(f"Email sent successfully to {user_email}")
        
        except Exception as e:
            logger.error(f"Failed to send email to {user_email}. Error: {str(e)}")
            continue
