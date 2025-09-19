from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend

from .models import User, Conversation, Message
from .serializers import (
    UserSerializer, ConversationSerializer, ConversationListSerializer,
    MessageSerializer
)
from .permissions import IsParticipantOfConversation, IsOwnerOrParticipant, IsMessageSender
from .filters import MessageFilter, ConversationFilter, UserFilter
from .pagination import MessagePagination, ConversationPagination, UserPagination


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet for User operations"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'user_id'
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = UserFilter
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering_fields = ['created_at', 'username']
    pagination_class = UserPagination
    
    def get_queryset(self):
        """
        Filter queryset to ensure users can only access appropriate data
        """
        if self.request.user.is_superuser:
            return User.objects.all()
        return User.objects.filter(user_id=self.request.user.user_id)


class ConversationViewSet(viewsets.ModelViewSet):
    """ViewSet for listing conversations and creating new conversations"""
    queryset = Conversation.objects.prefetch_related('participants', 'messages')
    lookup_field = 'conversation_id'
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsParticipantOfConversation]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = ConversationFilter
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    pagination_class = ConversationPagination
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ConversationListSerializer
        return ConversationSerializer
    
    def get_queryset(self):
        """
        Filter conversations to only show those where the user is a participant
        """
        return Conversation.objects.filter(
            participants__user_id=self.request.user.user_id
        ).prefetch_related('participants', 'messages')
    
    def create(self, request, *args, **kwargs):
        """Create a new conversation"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # Add the current user as a participant if not already included
            participant_ids = serializer.validated_data.get('participant_ids', [])
            if request.user.user_id not in participant_ids:
                participant_ids.append(request.user.user_id)
                serializer.validated_data['participant_ids'] = participant_ids
            
            conversation = serializer.save()
            response_serializer = ConversationSerializer(conversation)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def list(self, request, *args, **kwargs):
        """List all conversations for the authenticated user"""
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def retrieve(self, request, *args, **kwargs):
        """Get a specific conversation with all messages"""
        conversation = self.get_object()
        serializer = ConversationSerializer(conversation)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_participant(self, request, conversation_id=None):
        """Add a participant to the conversation"""
        conversation = self.get_object()
        user_id = request.data.get('user_id')
        
        try:
            user = User.objects.get(user_id=user_id)
            conversation.participants.add(user)
            return Response({'message': 'Participant added successfully'})
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'])
    def remove_participant(self, request, conversation_id=None):
        """Remove a participant from the conversation"""
        conversation = self.get_object()
        user_id = request.data.get('user_id')
        
        try:
            user = User.objects.get(user_id=user_id)
            conversation.participants.remove(user)
            return Response({'message': 'Participant removed successfully'})
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )


class MessageViewSet(viewsets.ModelViewSet):
    """ViewSet for listing messages and sending messages to existing conversations"""
    serializer_class = MessageSerializer
    lookup_field = 'message_id'
    authentication_classes = [JWTAuthentication]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = MessageFilter
    ordering_fields = ['sent_at']
    ordering = ['sent_at']
    pagination_class = MessagePagination
    
    def get_permissions(self):
        """
        Apply different permissions based on the action
        """
        if self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated, IsMessageSender]
        else:
            permission_classes = [IsAuthenticated, IsOwnerOrParticipant]
        
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        """
        Get messages that the user has access to (from conversations they participate in)
        """
        user_conversations = Conversation.objects.filter(
            participants__user_id=self.request.user.user_id
        )
        
        queryset = Message.objects.filter(
            conversation__in=user_conversations
        ).select_related('sender', 'conversation')
        
        return queryset
    
    def list(self, request, *args, **kwargs):
        """List all messages accessible to the user"""
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def create(self, request, *args, **kwargs):
        """Send a new message to an existing conversation"""
        # Set the sender to the current authenticated user
        request.data['sender_id'] = str(request.user.user_id)
        
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # Verify conversation exists
            conversation = serializer.validated_data['conversation']
            if not conversation:
                return Response(
                    {'error': 'Conversation not found'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Verify sender is participant in conversation
            if not conversation.participants.filter(user_id=request.user.user_id).exists():
                return Response(
                    {'error': 'You are not a participant in this conversation'}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Save message
            message = serializer.save(sender=request.user)
            response_serializer = MessageSerializer(message)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def retrieve(self, request, *args, **kwargs):
        """Get a specific message"""
        message = self.get_object()
        serializer = self.get_serializer(message)
        return Response(serializer.data)
    
    def update(self, request, *args, **kwargs):
        """Update a message (only allowed for the sender)"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)
    
    def destroy(self, request, *args, **kwargs):
        """Delete a message (only allowed for the sender)"""
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)