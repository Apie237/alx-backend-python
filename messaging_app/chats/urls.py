from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, ConversationViewSet, MessageViewSet

# Create a DefaultRouter instance
router = DefaultRouter()

# Register viewsets with the router
router.register(r'users', UserViewSet)
router.register(r'conversations', ConversationViewSet)
router.register(r'messages', MessageViewSet, basename='message')

# Include router URLs
urlpatterns = [
    path('', include(router.urls)),
]