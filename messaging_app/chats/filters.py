import django_filters
from django_filters import rest_framework as filters
from django.db.models import Q
from .models import Message, Conversation, User


class MessageFilter(filters.FilterSet):
    """
    Filter class for Message model to filter by conversation, user, and time range
    """
    conversation = filters.UUIDFilter(field_name='conversation__conversation_id')
    sender = filters.UUIDFilter(field_name='sender__user_id')
    sent_after = filters.DateTimeFilter(field_name='sent_at', lookup_expr='gte')
    sent_before = filters.DateTimeFilter(field_name='sent_at', lookup_expr='lte')
    date_range = filters.DateFromToRangeFilter(field_name='sent_at')
    message_contains = filters.CharFilter(field_name='message_body', lookup_expr='icontains')
    
    class Meta:
        model = Message
        fields = ['conversation', 'sender', 'sent_after', 'sent_before', 'date_range', 'message_contains']


class ConversationFilter(filters.FilterSet):
    """
    Filter class for Conversation model to filter by participants and creation date
    """
    participant = filters.UUIDFilter(method='filter_by_participant')
    created_after = filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    has_messages = filters.BooleanFilter(method='filter_has_messages')
    
    class Meta:
        model = Conversation
        fields = ['participant', 'created_after', 'created_before', 'has_messages']
    
    def filter_by_participant(self, queryset, name, value):
        """
        Filter conversations by specific participant
        """
        return queryset.filter(participants__user_id=value)
    
    def filter_has_messages(self, queryset, name, value):
        """
        Filter conversations that have or don't have messages
        """
        if value:
            return queryset.filter(messages__isnull=False).distinct()
        else:
            return queryset.filter(messages__isnull=True)


class UserFilter(filters.FilterSet):
    """
    Filter class for User model
    """
    email = filters.CharFilter(field_name='email', lookup_expr='iexact')
    role = filters.ChoiceFilter(choices=[('guest', 'Guest'), ('host', 'Host'), ('admin', 'Admin')])
    username = filters.CharFilter(field_name='username', lookup_expr='icontains')
    first_name = filters.CharFilter(field_name='first_name', lookup_expr='icontains')
    last_name = filters.CharFilter(field_name='last_name', lookup_expr='icontains')
    created_after = filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    
    class Meta:
        model = User
        fields = ['email', 'role', 'username', 'first_name', 'last_name', 'created_after', 'created_before']