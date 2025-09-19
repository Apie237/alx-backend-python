from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.cache import cache_page
from django.contrib.auth.decorators import login_required
from .models import Message


@login_required
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.user == user:
        user.delete()
        return JsonResponse({"status": "User deleted"})
    return JsonResponse({"error": "Unauthorized"}, status=403)


@cache_page(60)
@login_required
def message_list(request):
    """
    Retrieve all messages sent by the current user,
    along with their replies, optimized with select_related & prefetch_related.
    """
    messages = (
        Message.objects.filter(sender=request.user)
        .select_related("sender", "receiver")
        .prefetch_related("replies")
    )

    data = []
    for msg in messages:
        replies = [
            {
                "id": reply.id,
                "sender": reply.sender.username,
                "content": reply.content,
                "timestamp": reply.timestamp,
            }
            for reply in msg.replies.all()
        ]
        data.append(
            {
                "id": msg.id,
                "sender": msg.sender.username,
                "receiver": msg.receiver.username,
                "content": msg.content,
                "timestamp": msg.timestamp,
                "replies": replies,
            }
        )
    return JsonResponse(data, safe=False)


@login_required
def unread_messages(request):
    """
    Use custom manager to retrieve unread messages for the logged-in user.
    Optimized with `.only()` inside the manager.
    """
    unread_qs = Message.unread.unread_for_user(request.user)  # ✅ required check

    data = [
        {
            "id": msg.id,
            "sender": msg.sender.username,
            "content": msg.content,
            "timestamp": msg.timestamp,
        }
        for msg in unread_qs
    ]
    return JsonResponse(data, safe=False)
