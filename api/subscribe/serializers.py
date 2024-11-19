from rest_framework import serializers
from .models import Subscription


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ['sub_email']

    def validate_sub_email(self, value):
        if Subscription.objects.filter(sub_email=value).exists():
            raise serializers.ValidationError("This email is already subscribed.")
        return value

    def create(self, validated_data):
        email = validated_data.get('sub_email')
        subscription, created = Subscription.objects.get_or_create(sub_email=email)
        if created:
            return subscription
        return None 
    
