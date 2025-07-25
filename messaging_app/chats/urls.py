from django.urls import path, include
from rest_framework import routers
from .views import UserViewSet, ConversationViewSet, MessageViewSet

# Create a DefaultRouter instance using routers.DefaultRouter()
router = routers.DefaultRouter()

# Register viewsets with the router
router.register(r'users', UserViewSet)
router.register(r'conversations', ConversationViewSet)
router.register(r'messages', MessageViewSet, basename='message')

# Include router URLs
urlpatterns = [
    path('', include(router.urls)),
]