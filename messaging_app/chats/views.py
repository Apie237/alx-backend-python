from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import User, Conversation, Message
from .serializers import (
    UserSerializer, ConversationSerializer, ConversationListSerializer,
    MessageSerializer
)


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet for User operations"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'user_id'
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering_fields = ['created_at', 'username']


class ConversationViewSet(viewsets.ModelViewSet):
    """ViewSet for listing conversations and creating new conversations"""
    queryset = Conversation.objects.prefetch_related('participants', 'messages')
    lookup_field = 'conversation_id'
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ConversationListSerializer
        return ConversationSerializer
    
    def create(self, request, *args, **kwargs):
        """Create a new conversation"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            conversation = serializer.save()
            response_serializer = ConversationSerializer(conversation)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def list(self, request, *args, **kwargs):
        """List all conversations"""
        queryset = self.get_queryset()
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
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['sent_at']
    ordering = ['sent_at']
    
    def get_queryset(self):
        """Get messages, optionally filtered by conversation"""
        queryset = Message.objects.select_related('sender', 'conversation')
        conversation_id = self.request.query_params.get('conversation_id')
        
        if conversation_id:
            queryset = queryset.filter(conversation__conversation_id=conversation_id)
        
        return queryset
    
    def list(self, request, *args, **kwargs):
        """List all messages"""
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def create(self, request, *args, **kwargs):
        """Send a new message to an existing conversation"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # Verify sender exists
            sender_id = serializer.validated_data['sender_id']
            try:
                sender = User.objects.get(user_id=sender_id)
            except User.DoesNotExist:
                return Response(
                    {'error': 'Sender not found'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Verify conversation exists
            conversation = serializer.validated_data['conversation']
            if not conversation:
                return Response(
                    {'error': 'Conversation not found'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Verify sender is participant in conversation
            if not conversation.participants.filter(user_id=sender_id).exists():
                return Response(
                    {'error': 'Sender is not a participant in this conversation'}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Save message
            message = serializer.save(sender=sender)
            response_serializer = MessageSerializer(message)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def retrieve(self, request, *args, **kwargs):
        """Get a specific message"""
        message = self.get_object()
        serializer = self.get_serializer(message)
        return Response(serializer.data)