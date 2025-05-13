from django.urls import path

from .views import (
    ConversationListView,
    ConversationDetailView,
    ConversationMessagesView,
    ConversationMembersView,
)

urlpatterns = [
    path('conversations/', ConversationListView.as_view(), name='conversation-list'),
    path('conversations/<uuid:conversation_id>/', ConversationDetailView.as_view(), name='conversation-detail'),
    path('conversations/<uuid:conversation_id>/messages/', ConversationMessagesView.as_view(), name='conversation-messages'),
    path('conversations/<uuid:conversation_id>/members/', ConversationMembersView.as_view(), name='conversation-members'),
]