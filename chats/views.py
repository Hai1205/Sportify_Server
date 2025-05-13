from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q, Max, Prefetch, Count
from .models import Conversation, ConversationMember, Message
from django.utils import timezone
from .serializers import ConversationSerializer, MessageSerializer, ConversationMemberSerializer
from users.models import User
import logging
import uuid

logger = logging.getLogger(__name__)

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

class ConversationListView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            user = request.user
            
            member_conversations = ConversationMember.objects.filter(
                user=user
            ).values_list('conversation_id', flat=True)
            
            conversations = Conversation.objects.filter(
                id__in=member_conversations
            )
            
            conversations = conversations.annotate(
                last_message_time=Max('messages__created_at')
            ).order_by('-last_message_time')
            
            conversations = conversations.annotate(
                message_count=Count('messages')
            )
            
            serializer = ConversationSerializer(
                conversations, 
                many=True, 
                context={'user': user}
            )
            
            return Response({
                'status': 'success',
                'conversations': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error listing conversations: {str(e)}")
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def post(self, request):
        print("DEBUG request.user:", request.user, request.user.is_authenticated)
        try:
            conversation_type = request.data.get('type', 'direct')
            name = request.data.get('name')
            members = request.data.get('members', [])
            if conversation_type == 'direct':
                if len(members) != 1:
                    return Response({
                        'status': 'error',
                        'message': 'Direct conversations require exactly one other member'
                    }, status=status.HTTP_400_BAD_REQUEST)
                try:
                    other_user_id = members[0]
                    other_user = User.objects.get(id=other_user_id)
                except User.DoesNotExist:
                    return Response({
                        'status': 'error', 
                        'message': 'User not found'
                    }, status=status.HTTP_404_NOT_FOUND)
                conversation = Conversation.get_or_create_direct_conversation(request.user, other_user)
                
            else:  # Group conversation
                if not name:
                    return Response({
                        'status': 'error',
                        'message': 'Group conversations require a name'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                if not members:
                    return Response({
                        'status': 'error',
                        'message': 'Group conversations require at least one member'
                    }, status=status.HTTP_400_BAD_REQUEST)
                conversation = Conversation.objects.create(
                    name=name,
                    conversation_type='group'
                )
                ConversationMember.objects.create(
                    conversation=conversation,
                    user=request.user,
                    role='owner'
                )
                for member_id in members:
                    try:
                        user = User.objects.get(id=member_id)
                        if user.id != request.user.id:
                            ConversationMember.objects.create(
                                conversation=conversation,
                                user=user,
                                role='member'
                            )
                    except User.DoesNotExist:
                        logger.warning(f"User with id {member_id} not found when creating conversation")
            
            serializer = ConversationSerializer(conversation, context={'user': request.user})
            return Response({
                'status': 'success',
                'conversation': serializer.data
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Error creating conversation: {str(e)}")
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ConversationDetailView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, conversation_id):
        try:
            try:
                conversation = Conversation.objects.get(id=conversation_id)
            except Conversation.DoesNotExist:
                return Response({
                    'status': 'error',
                    'message': 'Conversation not found'
                }, status=status.HTTP_404_NOT_FOUND)
            if not ConversationMember.objects.filter(conversation=conversation, user=request.user).exists():
                return Response({
                    'status': 'error',
                    'message': 'You are not a member of this conversation'
                }, status=status.HTTP_403_FORBIDDEN)
            
            serializer = ConversationSerializer(conversation, context={'user': request.user})
            return Response({
                'status': 'success',
                'conversation': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error retrieving conversation details: {str(e)}")
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def patch(self, request, conversation_id):
        try:
            try:
                conversation = Conversation.objects.get(id=conversation_id)
            except Conversation.DoesNotExist:
                return Response({
                    'status': 'error',
                    'message': 'Conversation not found'
                }, status=status.HTTP_404_NOT_FOUND)
            member = ConversationMember.objects.filter(
                conversation=conversation, 
                user=request.user,
                role__in=['admin', 'owner']
            ).first()
            if not member:
                return Response({
                    'status': 'error',
                    'message': 'You do not have permission to update this conversation'
                }, status=status.HTTP_403_FORBIDDEN)
            if conversation.conversation_type == 'group' and 'name' in request.data:
                conversation.name = request.data['name']
                conversation.save()
            
            serializer = ConversationSerializer(conversation, context={'user': request.user})
            return Response({
                'status': 'success',
                'conversation': serializer.data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error updating conversation: {str(e)}")
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ConversationMessagesView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    
    def get(self, request, conversation_id):
        try:
            try:
                conversation = Conversation.objects.get(id=conversation_id)
            except Conversation.DoesNotExist:
                return Response({
                    'status': 'error',
                    'message': 'Conversation not found'
                }, status=status.HTTP_404_NOT_FOUND)
            if not ConversationMember.objects.filter(conversation=conversation, user=request.user).exists():
                return Response({
                    'status': 'error',
                    'message': 'You are not a member of this conversation'
                }, status=status.HTTP_403_FORBIDDEN)
           
            paginator = self.pagination_class()
            messages = Message.objects.filter(conversation=conversation).order_by('-created_at')
            result_page = paginator.paginate_queryset(messages, request)
            
            serializer = MessageSerializer(result_page, many=True)
            
            member = ConversationMember.objects.get(conversation=conversation, user=request.user)
            member.last_read_at = timezone.now()
            member.save()
            
            return paginator.get_paginated_response({
                'status': 'success',
                'messages': serializer.data
            })
            
        except Exception as e:
            logger.error(f"Error retrieving conversation messages: {str(e)}")
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def post(self, request, conversation_id):
        try:
            try:
                conversation = Conversation.objects.get(id=conversation_id)
            except Conversation.DoesNotExist:
                return Response({
                    'status': 'error',
                    'message': 'Conversation not found'
                }, status=status.HTTP_404_NOT_FOUND)
            if not ConversationMember.objects.filter(conversation=conversation, user=request.user).exists():
                return Response({
                    'status': 'error',
                    'message': 'You are not a member of this conversation'
                }, status=status.HTTP_403_FORBIDDEN)
            
            content = request.data.get('content')
            if not content:
                return Response({
                    'status': 'error',
                    'message': 'Message content is required'
                }, status=status.HTTP_400_BAD_REQUEST)
        
            message = Message.objects.create(
                conversation=conversation,
                sender=request.user,
                content=content
            )
            conversation.updated_at = timezone.now()
            conversation.save()
            
            serializer = MessageSerializer(message)
            return Response({
                'status': 'success',
                'message': serializer.data
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Error sending message: {str(e)}")
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ConversationMembersView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, conversation_id):
        try:
            try:
                conversation = Conversation.objects.get(id=conversation_id)
            except Conversation.DoesNotExist:
                return Response({
                    'status': 'error',
                    'message': 'Conversation not found'
                }, status=status.HTTP_404_NOT_FOUND)
            if not ConversationMember.objects.filter(conversation=conversation, user=request.user).exists():
                return Response({
                    'status': 'error',
                    'message': 'You are not a member of this conversation'
                }, status=status.HTTP_403_FORBIDDEN)
            
            members = ConversationMember.objects.filter(conversation=conversation)
            serializer = ConversationMemberSerializer(members, many=True)
            
            return Response({
                'status': 'success',
                'members': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error retrieving conversation members: {str(e)}")
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def post(self, request, conversation_id):
        try:
            try:
                conversation = Conversation.objects.get(id=conversation_id)
            except Conversation.DoesNotExist:
                return Response({
                    'status': 'error',
                    'message': 'Conversation not found'
                }, status=status.HTTP_404_NOT_FOUND)
            
            if conversation.conversation_type == 'direct':
                return Response({
                    'status': 'error',
                    'message': 'Cannot add members to direct conversations'
                }, status=status.HTTP_400_BAD_REQUEST)
        
            member = ConversationMember.objects.filter(
                conversation=conversation, 
                user=request.user,
                role__in=['admin', 'owner']
            ).first()
            
            if not member:
                return Response({
                    'status': 'error',
                    'message': 'You do not have permission to add members'
                }, status=status.HTTP_403_FORBIDDEN)
            
            user_id = request.data.get('user_id')
            if not user_id:
                return Response({
                    'status': 'error',
                    'message': 'User ID is required'
                }, status=status.HTTP_400_BAD_REQUEST)
           
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return Response({
                    'status': 'error',
                    'message': 'User not found'
                }, status=status.HTTP_404_NOT_FOUND)
            
            if ConversationMember.objects.filter(conversation=conversation, user=user).exists():
                return Response({
                    'status': 'error',
                    'message': 'User is already a member of this conversation'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            member = ConversationMember.objects.create(
                conversation=conversation,
                user=user,
                role='member'
            )
            
            serializer = ConversationMemberSerializer(member)
            return Response({
                'status': 'success',
                'member': serializer.data
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Error adding conversation member: {str(e)}")
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
