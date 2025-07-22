from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
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


class ConversationViewSet(viewsets.ModelViewSet):
    """ViewSet for Conversation operations"""
    queryset = Conversation.objects.prefetch_related('participants', 'messages')
    lookup_field = 'conversation_id'
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ConversationListSerializer
        return ConversationSerializer
    
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
    """ViewSet for Message operations"""
    serializer_class = MessageSerializer
    lookup_field = 'message_id'
    
    def get_queryset(self):
        queryset = Message.objects.select_related('sender', 'conversation')
        conversation_id = self.request.query_params.get('conversation_id')
        
        if conversation_id:
            queryset = queryset.filter(conversation__conversation_id=conversation_id)
        
        return queryset
    
    def create(self, request, *args, **kwargs):
        """Create a new message"""
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
