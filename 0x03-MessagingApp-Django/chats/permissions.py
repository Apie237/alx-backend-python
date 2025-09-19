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


# Enhanced versions with method-specific checks:

class IsMessageSenderForModification(permissions.BasePermission):
    """
    Permission to allow only message senders to update/delete their messages,
    but allow participants to read messages
    """
    
    def has_permission(self, request, view):
        """
        Allow only authenticated users
        """
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        """
        Check permissions based on HTTP method
        """
        if isinstance(obj, Message):
            # For modification operations, only the sender can proceed
            if request.method in ["PUT", "PATCH", "DELETE"]:
                return obj.sender.user_id == request.user.user_id
            
            # For read operations, any participant can access
            elif request.method in ["GET", "HEAD", "OPTIONS"]:
                return obj.conversation.participants.filter(user_id=request.user.user_id).exists()
        
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
            
            # Maybe only the creator can delete? Or any participant?
            elif request.method == "DELETE":
                # Option 1: Only creator can delete
                # return obj.created_by.user_id == request.user.user_id
                
                # Option 2: Any participant can delete
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


# Alternative: Permission class that combines multiple checks
class ChatPermissions(permissions.BasePermission):
    """
    Unified permission class that handles both conversations and messages
    with method-specific logic
    """
    
    def has_permission(self, request, view):
        """
        Allow only authenticated users
        """
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        """
        Handle permissions for both Conversation and Message objects
        """
        # Handle Message permissions
        if isinstance(obj, Message):
            is_participant = obj.conversation.participants.filter(user_id=request.user.user_id).exists()
            is_sender = obj.sender.user_id == request.user.user_id
            
            if request.method in ["GET", "HEAD", "OPTIONS"]:
                return is_participant
            elif request.method in ["PUT", "PATCH", "DELETE"]:
                return is_sender
        
        # Handle Conversation permissions
        elif isinstance(obj, Conversation):
            is_participant = obj.participants.filter(user_id=request.user.user_id).exists()
            
            if request.method in ["GET", "HEAD", "OPTIONS", "PUT", "PATCH"]:
                return is_participant
            elif request.method == "DELETE":
                # Decide your business logic here
                return is_participant
        
        return False