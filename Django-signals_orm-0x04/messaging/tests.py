from django.test import TestCase
from django.contrib.auth.models import User
from .models import Message, Notification


class MessagingTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="alice", password="password123")
        self.user2 = User.objects.create_user(username="bob", password="password123")

    def test_message_creates_notification(self):
        msg = Message.objects.create(sender=self.user1, receiver=self.user2, content="Hello Bob!")
        self.assertTrue(Notification.objects.filter(user=self.user2, message=msg).exists())

    def test_edit_message_creates_history(self):
        msg = Message.objects.create(sender=self.user1, receiver=self.user2, content="Hello Bob!")
        msg.content = "Hello Bob, edited!"
        msg.save()
        self.assertEqual(msg.history.count(), 1)
