# =============================================================================
# messaging_app/settings.py
# =============================================================================
"""
Django settings for messaging_app project.
"""

from pathlib import Path
from datetime import timedelta

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-tij9cxobcci+#zi93u_r9h&4ve3j@_x%g+(^)q6#0wydz0xy5o'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt',
    'django_filters',
    'chats',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'messaging_app.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'messaging_app.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Django REST Framework Configuration
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.OrderingFilter',
        'rest_framework.filters.SearchFilter',
    ],
}

# JWT Configuration
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': False,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,
    'JWK_URL': None,
    'LEEWAY': 0,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'user_id',
    'USER_ID_CLAIM': 'user_id',
    'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
    'TOKEN_USER_CLASS': 'rest_framework_simplejwt.models.TokenUser',
    'JTI_CLAIM': 'jti',
    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=5),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),
}

# Tell Django to use our custom User model
AUTH_USER_MODEL = 'chats.User'


# =============================================================================
# messaging_app/urls.py
# =============================================================================
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('chats.urls')),
]


# =============================================================================
# chats/models.py
# =============================================================================
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
import uuid


class User(AbstractUser):
    """Custom User model"""
    user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    is_online = models.BooleanField(default=False)
    last_seen = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return f"{self.username} ({self.email})"

    class Meta:
        db_table = 'users'


class Conversation(models.Model):
    """Model for conversations/chat rooms"""
    conversation_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200, blank=True)
    is_group = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_conversations')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Conversation: {self.title or f'Chat {self.conversation_id}'}"

    @property
    def participant_count(self):
        return self.participants.count()

    @property
    def last_message(self):
        return self.messages.order_by('-created_at').first()

    class Meta:
        db_table = 'conversations'
        ordering = ['-updated_at']


class ConversationParticipant(models.Model):
    """Model for conversation participants"""
    participant_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='participants')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conversation_participations')
    joined_at = models.DateTimeField(auto_now_add=True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'conversation_participants'
        unique_together = ['conversation', 'user']

    def __str__(self):
        return f"{self.user.username} in {self.conversation}"


class Message(models.Model):
    """Model for messages"""
    message_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField()
    message_type = models.CharField(
        max_length=20,
        choices=[
            ('text', 'Text'),
            ('image', 'Image'),
            ('file', 'File'),
            ('system', 'System'),
        ],
        default='text'
    )
    is_edited = models.BooleanField(default=False)
    edited_at = models.DateTimeField(null=True, blank=True)
    reply_to = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='replies')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Message from {self.sender.username}: {self.content[:50]}"

    def save(self, *args, **kwargs):
        if self.pk and self.is_edited:
            self.edited_at = timezone.now()
        super().save(*args, **kwargs)
        # Update conversation's updated_at timestamp
        self.conversation.updated_at = timezone.now()
        self.conversation.save(update_fields=['updated_at'])

    class Meta:
        db_table = 'messages'
        ordering = ['created_at']


class MessageRead(models.Model):
    """Model to track message read status"""
    read_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='read_by')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='read_messages')
    read_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'message_reads'
        unique_together = ['message', 'user']

    def __str__(self):
        return f"{self.user.username} read {self.message.message_id}"


# =============================================================================
# chats/permissions.py
# =============================================================================
from rest_framework import permissions
from .models import Conversation, Message


class IsParticipantOfConversation(permissions.BasePermission):
    """
    Custom permission to only allow participants of a conversation to access it.
    """
    
    def has_permission(self, request, view):
        """
        Allow only authenticated users to access the API
        """
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        """
        Object-level permission to only allow participants to access conversations and messages
        """
        # If the object is a Conversation
        if isinstance(obj, Conversation):
            return obj.participants.filter(user_id=request.user.user_id).exists()
        
        # If the object is a Message
        if isinstance(obj, Message):
            return obj.conversation.participants.filter(user_id=request.user.user_id).exists()
        
        # Default to False for other object types
        return False


class IsOwnerOrParticipant(permissions.BasePermission):
    """
    Permission to allow users to access their own messages and conversations
    """
    
    def has_permission(self, request, view):
        """
        Allow only authenticated users
        """
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        """
        Check if user is owner or participant
        """
        # For Message objects
        if isinstance(obj, Message):
            # User can access if they are the sender or a participant in the conversation
            return (obj.sender.user_id == request.user.user_id or
                    obj.conversation.participants.filter(user_id=request.user.user_id).exists())
        
        # For Conversation objects
        if isinstance(obj, Conversation):
            # User can access if they are a participant
            return obj.participants.filter(user_id=request.user.user_id).exists()
        
        return False


class MessagePermissions(permissions.BasePermission):
    """
    Comprehensive permission class for messages with method-specific rules
    """
    
    def has_permission(self, request, view):
        """
        Allow only authenticated users
        """
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        """
        Method-specific permissions for messages
        """
        if isinstance(obj, Message):
            # Any conversation participant can read messages
            if request.method in ["GET", "HEAD", "OPTIONS"]:
                return obj.conversation.participants.filter(user_id=request.user.user_id).exists()
            
            # Only the message sender can update their own messages
            elif request.method in ["PUT", "PATCH"]:
                return obj.sender.user_id == request.user.user_id
            
            # Only the message sender can delete their own messages
            elif request.method == "DELETE":
                return obj.sender.user_id == request.user.user_id
        
        return False


class ConversationPermissions(permissions.BasePermission):
    """
    Comprehensive permission class for conversations with method-specific rules
    """
    
    def has_permission(self, request, view):
        """
        Allow only authenticated users
        """
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        """
        Method-specific permissions for conversations
        """
        if isinstance(obj, Conversation):
            # All participants can read conversation details
            if request.method in ["GET", "HEAD", "OPTIONS"]:
                return obj.participants.filter(user_id=request.user.user_id).exists()
            
            # Only participants can update conversation (e.g., change title)
            elif request.method in ["PUT", "PATCH"]:
                return obj.participants.filter(user_id=request.user.user_id).exists()
            
            # Any participant can delete (you might want to restrict this further)
            elif request.method == "DELETE":
                return obj.participants.filter(user_id=request.user.user_id).exists()
        
        return False


# =============================================================================
# chats/serializers.py
# =============================================================================
from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, Conversation, ConversationParticipant, Message, MessageRead


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['user_id', 'username', 'email', 'first_name', 'last_name', 
                 'is_online', 'last_seen', 'created_at', 'password']
        extra_kwargs = {
            'password': {'write_only': True},
            'user_id': {'read_only': True},
            'created_at': {'read_only': True},
            'last_seen': {'read_only': True},
        }
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user
    
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        if password:
            instance.set_password(password)
        
        instance.save()
        return instance


class UserPublicSerializer(serializers.ModelSerializer):
    """Public serializer for User model (without sensitive data)"""
    
    class Meta:
        model = User
        fields = ['user_id', 'username', 'first_name', 'last_name', 'is_online', 'last_seen']


class ConversationParticipantSerializer(serializers.ModelSerializer):
    """Serializer for ConversationParticipant model"""
    user = UserPublicSerializer(read_only=True)
    user_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = ConversationParticipant
        fields = ['participant_id', 'user', 'user_id', 'joined_at', 'is_admin', 'is_active']
        read_only_fields = ['participant_id', 'joined_at']


class MessageReadSerializer(serializers.ModelSerializer):
    """Serializer for MessageRead model"""
    user = UserPublicSerializer(read_only=True)
    
    class Meta:
        model = MessageRead
        fields = ['read_id', 'user', 'read_at']


class MessageSerializer(serializers.ModelSerializer):
    """Serializer for Message model"""
    sender = UserPublicSerializer(read_only=True)
    read_by = MessageReadSerializer(many=True, read_only=True)
    reply_to_message = serializers.SerializerMethodField()
    
    class Meta:
        model = Message
        fields = ['message_id', 'conversation', 'sender', 'content', 'message_type',
                 'is_edited', 'edited_at', 'reply_to', 'reply_to_message', 'read_by',
                 'created_at', 'updated_at']
        read_only_fields = ['message_id', 'sender', 'is_edited', 'edited_at', 'created_at', 'updated_at']
    
    def get_reply_to_message(self, obj):
        if obj.reply_to:
            return {
                'message_id': obj.reply_to.message_id,
                'content': obj.reply_to.content[:100],
                'sender': obj.reply_to.sender.username
            }
        return None
    
    def create(self, validated_data):
        validated_data['sender'] = self.context['request'].user
        return super().create(validated_data)


class ConversationSerializer(serializers.ModelSerializer):
    """Serializer for Conversation model"""
    participants = ConversationParticipantSerializer(many=True, read_only=True)
    participant_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=False
    )
    created_by = UserPublicSerializer(read_only=True)
    participant_count = serializers.ReadOnlyField()
    last_message = MessageSerializer(read_only=True)
    
    class Meta:
        model = Conversation
        fields = ['conversation_id', 'title', 'is_group', 'created_by', 'participants',
                 'participant_ids', 'participant_count', 'last_message', 'created_at', 'updated_at']
        read_only_fields = ['conversation_id', 'created_by', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        participant_ids = validated_data.pop('participant_ids', [])
        validated_data['created_by'] = self.context['request'].user
        
        conversation = Conversation.objects.create(**validated_data)
        
        # Add creator as participant
        ConversationParticipant.objects.create(
            conversation=conversation,
            user=self.context['request'].user,
            is_admin=True
        )
        
        # Add other participants
        for user_id in participant_ids:
            try:
                user = User.objects.get(user_id=user_id)
                ConversationParticipant.objects.create(
                    conversation=conversation,
                    user=user
                )
            except User.DoesNotExist:
                pass
        
        return conversation


class LoginSerializer(serializers.Serializer):
    """Serializer for user login"""
    username = serializers.CharField()
    password = serializers.CharField()
    
    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        
        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise serializers.ValidationError('Invalid credentials')
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled')
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError('Must include username and password')


# =============================================================================
# chats/views.py
# =============================================================================
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import login
from django.utils import timezone
from django.db.models import Q, Prefetch
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter

from .models import User, Conversation, ConversationParticipant, Message, MessageRead
from .serializers import (
    UserSerializer, UserPublicSerializer, ConversationSerializer,
    MessageSerializer, LoginSerializer, ConversationParticipantSerializer
)
from .permissions import ConversationPermissions, MessagePermissions


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet for User model"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['username', 'first_name', 'last_name', 'email']
    ordering_fields = ['username', 'created_at', 'last_seen']
    ordering = ['-last_seen']
    
    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return UserPublicSerializer
        return UserSerializer
    
    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user profile"""
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['put', 'patch'])
    def update_profile(self, request):
        """Update current user profile"""
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def login(self, request):
        """User login endpoint"""
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            user.last_seen = timezone.now()
            user.is_online = True
            user.save(update_fields=['last_seen', 'is_online'])
            
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': UserSerializer(user).data
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def logout(self, request):
        """User logout endpoint"""
        request.user.is_online = False
        request.user.last_seen = timezone.now()
        request.user.save(update_fields=['is_online', 'last_seen'])
        return Response({'message': 'Logged out successfully'})


class ConversationViewSet(viewsets.ModelViewSet):
    """ViewSet for Conversation model"""
    serializer_class = ConversationSerializer
    permission_classes = [ConversationPermissions]
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_fields = ['is_group']
    search_fields = ['title']
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['-updated_at']
    
    def get_queryset(self):
        return Conversation.objects.filter(
            participants__user=self.request.user
        ).prefetch_related(
            'participants__user',
            Prefetch('messages', queryset=Message.objects.order_by('-created_at')[:1])
        ).distinct()
    
    @action(detail=True, methods=['post'])
    def add_participant(self, request, pk=None):
        """Add a participant to the conversation"""
        conversation = self.get_object()
        user_id = request.data.get('user_id')
        
        if not user_id:
            return Response({'error': 'user_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(user_id=user_id)
            participant, created = ConversationParticipant.objects.get_or_create(
                conversation=conversation,
                user=user,
                defaults={'is_active': True}
            )
            
            if created:
                serializer = ConversationParticipantSerializer(participant)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response({'message': 'User is already a participant'}, status=status.HTTP_200_OK)
        
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['post'])
    def remove_participant(self, request, pk=None):
        """Remove a participant from the conversation"""
        conversation = self.get_object()
        user_id = request.data.get('user_id')
        
        if not user_id:
            return Response({'error': 'user_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            participant = ConversationParticipant.objects.get(
                conversation=conversation,
                user__user_id=user_id
            )
            participant.delete()
            return Response({'message': 'Participant removed successfully'})
        
        except ConversationParticipant.DoesNotExist:
            return Response({'error': 'Participant not found'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        """Get messages for a specific conversation"""
        conversation = self.get_object()
        messages = Message.objects.filter(conversation=conversation).order_by('-created_at')
        
        # Apply pagination
        page = self.paginate_queryset(messages)
        if page is not None:
            serializer = MessageSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def leave(self, request, pk=None):
        """Leave the conversation"""
        conversation = self.get_object()
        try:
            participant = ConversationParticipant.objects.get(
                conversation=conversation,
                user=request.user
            )
            participant.delete()
            return Response({'message': 'Left conversation successfully'})
        except ConversationParticipant.DoesNotExist:
            return Response({'error': 'Not a participant'}, status=status.HTTP_400_BAD_REQUEST)


class MessageViewSet(viewsets.ModelViewSet):
    """ViewSet for Message model"""
    serializer_class = MessageSerializer
    permission_classes = [MessagePermissions]
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_fields = ['message_type']
    search_fields = ['content']
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        return Message.objects.filter(
            conversation__participants__user=self.request.user
        ).select_related('sender', 'conversation', 'reply_to').prefetch_related('read_by__user')
    
    def perform_update(self, serializer):
        """Mark message as edited when updated"""
        serializer.save(is_edited=True, edited_at=timezone.now())
    
    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        """Mark a message as read"""
        message = self.get_object()
        read_receipt, created = MessageRead.objects.get_or_create(
            message=message,
            user=request.user
        )
        
        if created:
            return Response({'message': 'Message marked as read'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'message': 'Message already marked as read'}, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def unread(self, request):
        """Get unread messages for the current user"""
        user_conversations = Conversation.objects.filter(participants__user=request.user)
        unread_messages = Message.objects.filter(
            conversation__in=user_conversations
        ).exclude(
            Q(read_by__user=request.user) | Q(sender=request.user)
        ).order_by('-created_at')
        
        # Apply pagination
        page = self.paginate_queryset(unread_messages)
        if page is not None:
            serializer = MessageSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = MessageSerializer(unread_messages, many=True)
        return Response(serializer.data)


# =============================================================================
# chats/urls.py
# =============