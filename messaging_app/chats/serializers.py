from rest_framework import serializers
from rest_framework.serializers import ValidationError
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

    def validate_username(self, value):
        """Custom validation for username"""
        if len(value) < 3:
            raise ValidationError("Username must be at least 3 characters long")
        return value

    def validate_email(self, value):
        """Custom validation for email"""
        if User.objects.filter(email=value).exists():
            raise ValidationError("User with this email already exists")
        return value


class MessageSerializer(serializers.ModelSerializer):
    """Serializer for Message model"""
    sender = UserSerializer(read_only=True)
    sender_id = serializers.UUIDField(write_only=True)
    message_body = serializers.CharField(max_length=1000, min_length=1)
    
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
            raise ValidationError("Message cannot be empty or contain only whitespace")
        return value.strip()

    def validate_sender_id(self, value):
        """Validate that sender exists"""
        try:
            User.objects.get(user_id=value)
        except User.DoesNotExist:
            raise ValidationError("Invalid sender ID")
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
            raise ValidationError("A conversation must have at least 2 participants")
        
        if len(set(value)) != len(value):
            raise ValidationError("Duplicate participants are not allowed")
        
        # Check if all participants exist
        existing_users = User.objects.filter(user_id__in=value)
        if existing_users.count() != len(value):
            raise ValidationError("One or more participant IDs are invalid")
        
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
    participant_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = [
            'conversation_id', 'participants', 'participant_count',
            'last_message', 'created_at'
        ]

    def get_last_message(self, obj):
        """Get the last message in the conversation"""
        last_message = obj.messages.last()
        if last_message:
            return {
                'message_body': last_message.message_body,
                'sent_at': last_message.sent_at,
                'sender': last_message.sender.username
            }
        return None

    def get_participant_count(self, obj):
        """Get the number of participants in the conversation"""
        return obj.participants.count()


class MessageCreateSerializer(serializers.ModelSerializer):
    """Specialized serializer for creating messages"""
    message_body = serializers.CharField(max_length=1000, min_length=1)
    
    class Meta:
        model = Message
        fields = ['conversation', 'message_body', 'sender_id']

    def validate_message_body(self, value):
        """Custom validation for message body"""
        if not value.strip():
            raise ValidationError("Message cannot be empty or contain only whitespace")
        return value.strip()

    def validate(self, attrs):
        """Cross-field validation"""
        conversation = attrs.get('conversation')
        sender_id = attrs.get('sender_id')
        
        if conversation and sender_id:
            # Check if sender is a participant in the conversation
            if not conversation.participants.filter(user_id=sender_id).exists():
                raise ValidationError("Sender must be a participant in the conversation")
        
        return attrs


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile with additional fields"""
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    
    class Meta:
        model = User
        fields = [
            'user_id', 'username', 'first_name', 'last_name',
            'full_name', 'email', 'phone_number', 'role', 'created_at'
        ]
        read_only_fields = ['user_id', 'created_at', 'full_name']

    def validate_phone_number(self, value):
        """Custom validation for phone number"""
        if value and len(value) < 10:
            raise ValidationError("Phone number must be at least 10 digits")
        return value