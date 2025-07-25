from rest_framework import serializers
from .models import User, Conversation, Message


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    
    class Meta:
        model = User
        fields = [
            'user_id', 'username', 'first_name', 'last_name', 
            'email', 'phone_number', 'role', 'created_at'
        ]
        read_only_fields = ['user_id', 'created_at']
    
    def validate_email(self, value):
        """Custom validation for email field"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value
    
    def validate_username(self, value):
        """Custom validation for username field"""
        if len(value) < 3:
            raise serializers.ValidationError("Username must be at least 3 characters long.")
        return value


class MessageSerializer(serializers.ModelSerializer):
    """Serializer for Message model"""
    sender = UserSerializer(read_only=True)
    sender_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = Message
        fields = [
            'message_id', 'sender', 'sender_id', 'conversation', 
            'message_body', 'sent_at'
        ]
        read_only_fields = ['message_id', 'sent_at']
    
    def validate_message_body(self, value):
        """Custom validation for message body"""
        if not value.strip():
            raise serializers.ValidationError("Message body cannot be empty.")
        if len(value) > 1000:
            raise serializers.ValidationError("Message body cannot exceed 1000 characters.")
        return value


class ConversationSerializer(serializers.ModelSerializer):
    """Serializer for Conversation model with nested messages"""
    participants = UserSerializer(many=True, read_only=True)
    participant_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=False
    )
    messages = MessageSerializer(many=True, read_only=True)
    
    class Meta:
        model = Conversation
        fields = [
            'conversation_id', 'participants', 'participant_ids',
            'messages', 'created_at'
        ]
        read_only_fields = ['conversation_id', 'created_at']
    
    def validate_participant_ids(self, value):
        """Custom validation for participant IDs"""
        if len(value) < 2:
            raise serializers.ValidationError("A conversation must have at least 2 participants.")
        if len(value) > 50:
            raise serializers.ValidationError("A conversation cannot have more than 50 participants.")
        
        # Check if all participant IDs exist
        existing_users = User.objects.filter(user_id__in=value)
        if len(existing_users) != len(value):
            raise serializers.ValidationError("One or more participant IDs do not exist.")
        
        return value
    
    def create(self, validated_data):
        participant_ids = validated_data.pop('participant_ids', [])
        conversation = Conversation.objects.create(**validated_data)
        
        if participant_ids:
            participants = User.objects.filter(user_id__in=participant_ids)
            conversation.participants.set(participants)
        
        return conversation


class ConversationListSerializer(serializers.ModelSerializer):
    """Simplified serializer for listing conversations"""
    participants = UserSerializer(many=True, read_only=True)
    last_message = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = [
            'conversation_id', 'participants', 'last_message', 'created_at'
        ]
    
    def get_last_message(self, obj):
        last_message = obj.messages.last()
        if last_message:
            return {
                'message_body': last_message.message_body,
                'sent_at': last_message.sent_at,
                'sender': last_message.sender.username
            }
        return None