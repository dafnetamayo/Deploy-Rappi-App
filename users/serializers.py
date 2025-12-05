# users/serializers.py
from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Profile

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['phone', 'default_address']

class UserMeSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'profile']

    def update(self, instance, validated_data):
        # nested update for profile and user fields
        profile_data = validated_data.pop('profile', {})
        for attr, val in validated_data.items():
            setattr(instance, attr, val)
        instance.save()

        if profile_data:
            prof = getattr(instance, 'profile', None)
            if prof is None:
                prof = Profile.objects.create(user=instance)
            for attr, val in profile_data.items():
                setattr(prof, attr, val)
            prof.save()

        return instance