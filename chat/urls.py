from django.urls import path, include
from rest_framework.routers import DefaultRouter
from chat.views import ChatRoomViewSet

router = DefaultRouter()
router.register('rooms', ChatRoomViewSet, basename='chat-room')

urlpatterns = [
    path('', include(router.urls)),
]
