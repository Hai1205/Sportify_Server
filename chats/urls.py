from django.urls import path
from .views import GetAllMessageView, getMessageView

urlpatterns = [
    path('', GetAllMessageView.as_view(), name='get-all-message'),
    path('get-message/<uuid:senderId>/<uuid:receiverId>/', getMessageView.as_view(), name='get-message'),
]