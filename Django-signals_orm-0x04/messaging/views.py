from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect
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


@cache_page(60)  # Cache for 60 seconds
@login_required
def message_list(request):
    messages = Message.objects.filter(receiver=request.user).select_related("sender")
    data = [
        {"id": msg.id, "sender": msg.sender.username, "content": msg.content, "timestamp": msg.timestamp}
        for msg in messages
    ]
    return JsonResponse(data, safe=False)
