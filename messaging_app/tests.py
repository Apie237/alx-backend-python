# messaging_app/messages/tests.py
import pytest
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Message


class MessageModelTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='testpass123')
        self.user2 = User.objects.create_user(username='user2', password='testpass123')
    
    def test_create_message(self):
        message = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Hello, this is a test message!"
        )
        self.assertEqual(message.sender, self.user1)
        self.assertEqual(message.receiver, self.user2)
        self.assertEqual(message.content, "Hello, this is a test message!")
        self.assertFalse(message.is_read)
    
    def test_message_str_representation(self):
        message = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Hello, this is a test message!"
        )
        expected_str = f"From {self.user1.username} to {self.user2.username}: Hello, this is a test message!..."
        self.assertEqual(str(message), expected_str)


class MessageAPITest(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='testpass123')
        self.user2 = User.objects.create_user(username='user2', password='testpass123')
        self.message = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Test message content"
        )
    
    def test_get_messages_unauthenticated(self):
        url = '/api/messages/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_get_messages_authenticated(self):
        self.client.force_authenticate(user=self.user1)
        url = '/api/messages/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_get_inbox_messages(self):
        self.client.force_authenticate(user=self.user2)
        url = '/api/messages/inbox/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_get_sent_messages(self):
        self.client.force_authenticate(user=self.user1)
        url = '/api/messages/sent/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)


# messaging_app/tests/test_integration.py
import pytest
from django.test import TestCase, TransactionTestCase
from django.contrib.auth.models import User
from messages.models import Message


@pytest.mark.django_db
class TestMessageIntegration:
    def test_user_can_send_message(self):
        user1 = User.objects.create_user(username='sender', password='testpass123')
        user2 = User.objects.create_user(username='receiver', password='testpass123')
        
        message = Message.objects.create(
            sender=user1,
            receiver=user2,
            content="Integration test message"
        )
        
        assert message.id is not None
        assert message.sender == user1
        assert message.receiver == user2
        assert not message.is_read
    
    def test_user_can_receive_multiple_messages(self):
        user1 = User.objects.create_user(username='sender1', password='testpass123')
        user2 = User.objects.create_user(username='sender2', password='testpass123')
        receiver = User.objects.create_user(username='receiver', password='testpass123')
        
        Message.objects.create(sender=user1, receiver=receiver, content="Message 1")
        Message.objects.create(sender=user2, receiver=receiver, content="Message 2")
        
        received_messages = Message.objects.filter(receiver=receiver)
        assert received_messages.count() == 2


# messaging_app/conftest.py
import pytest
from django.contrib.auth.models import User


@pytest.fixture
def test_user():
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )


@pytest.fixture
def another_user():
    return User.objects.create_user(
        username='anotheruser',
        email='another@example.com',
        password='testpass123'
    )


# messaging_app/pytest.ini
[tool:pytest]
DJANGO_SETTINGS_MODULE = messaging_app.settings_test
python_files = tests.py test_*.py *_tests.py
addopts = --tb=short --strict-markers
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks tests as integration tests