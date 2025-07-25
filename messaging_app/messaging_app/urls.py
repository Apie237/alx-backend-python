from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('chats.urls')),  # Include chats app URLs with 'api' prefix
    path('api-auth/', include('rest_framework.urls')),  # Add DRF authentication URLs
]