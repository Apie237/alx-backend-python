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


class IsMessageSender(permissions.BasePermission):
    """
    Permission to allow only message senders to update/delete their messages
    """
    
    def has_permission(self, request, view):
        """
        Allow only authenticated users
        """
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        """
        Only allow message sender to update/delete the message
        """
        if isinstance(obj, Message):
            return obj.sender.user_id == request.user.user_id
        return False