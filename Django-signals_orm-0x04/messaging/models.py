from django.db import models
from django.contrib.auth.models import User
from .managers import UnreadMessagesManager   # ✅ import custom manager


class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_messages")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_messages")
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    edited = models.BooleanField(default=False)
    read = models.BooleanField(default=False)
    parent_message = models.ForeignKey(
        'self', null=True, blank=True, on_delete=models.CASCADE, related_name="replies"
    )
    edited_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL, related_name="edited_messages"
    )

    # Managers
    objects = models.Manager()          # default manager
    unread = UnreadMessagesManager()    # ✅ custom manager

    def __str__(self):
        return f"From {self.sender} to {self.receiver}: {self.content[:20]}"
