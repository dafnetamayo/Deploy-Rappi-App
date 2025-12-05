from django.shortcuts import render
from django.contrib.auth.models import User
from rest_framework import permissions, viewsets
from .serializers import UserMeSerializer

# Create your views here.
class MeViewSet(viewsets.ModelViewSet):
    # expose retrieve/update for current user
    serializer_class = UserMeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return User.objects.filter(id=self.request.user.id)