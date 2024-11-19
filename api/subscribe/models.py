from django.db import models
import uuid

class Subscription(models.Model):
    sub_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    sub_email = models.EmailField(unique=True)
    def __str__(self):
        return self.sub_email


