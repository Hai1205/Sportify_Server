from rest_framework.permissions import IsAdminUser
from .serializers import UserSerializer, FullInfoUserSerializer, UpdateUserSerializer, ResponseUpdateUserToArtistSerializer, RequireUpdateUserToArtistSerializer
from .models import User
from rest_framework.generics import GenericAPIView
from django.shortcuts import get_object_or_404
from django.http import JsonResponse

class GetAllUserView(GenericAPIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        try:
            users = User.objects.all()
            serializer = FullInfoUserSerializer(users, many=True)
        
            return JsonResponse({
                "status": 200,
                "message": "Get all user successfully",
                "users": serializer.data
            }, safe=False, status=200)
        except Exception as e:
            return JsonResponse({
                "status": 500,
                "message": str(e)
            }, status=500)

class GetSuggestedUserView(GenericAPIView):
    def get(self, request, userId):
        try:
            currentUser = get_object_or_404(User, id=userId)

            # Lấy danh sách ID người dùng mà currentUser đang follow
            followingIds = currentUser.following.values_list('id', flat=True)

            # Lọc danh sách người dùng gợi ý
            userLimit = 10
            suggestedUsers = User.objects.exclude(id__in=followingIds).exclude(id=userId).order_by('?')[:userLimit]

            serializer = UserSerializer(suggestedUsers, many=True)

            return JsonResponse({
                "status": 200,
                "message": "Get suggested user successfully",
                "users": serializer.data
            }, status=200)

        except Exception as e:
            return JsonResponse({
                "status": 500,
                "message": str(e)
            }, status=500)

class FollowUserView(GenericAPIView):
    def post(self, request, currentUserId, opponentId):
        try:
            if currentUserId == opponentId:
                return JsonResponse({
                    "status": 400,
                    "message": "You can't follow/unfollow yourself"
                }, status=400)

            currentUser = get_object_or_404(User, id=currentUserId)
            opponent = get_object_or_404(User, id=opponentId)

            if opponent in currentUser.following.all():
                # Nếu đã follow thì hủy follow
                currentUser.following.remove(opponent)
                opponent.followers.remove(currentUser)
                message = "unfollowed"
            else:
                # Nếu chưa follow thì thêm vào danh sách follow
                currentUser.following.add(opponent)
                opponent.followers.add(currentUser)
                message = "followed"

            currentUser.save()
            opponent.save()
            
            serializer = FullInfoUserSerializer(currentUser)

            return JsonResponse({
                "status": 200,
                "message": f"User {message} successfully",
                "user": serializer.data
            }, status=200)

        except Exception as e:
            return JsonResponse({
                "status": 500,
                "message": str(e)
            }, status=500)

class GetUserView(GenericAPIView):
    def get(self, request, userId):
        try:
            user = get_object_or_404(User, id=userId)
            serializer = FullInfoUserSerializer(user)
        
            return JsonResponse({
                "status": 200,
                "message": "Get user successfully",
                "user": serializer.data
            }, safe=False, status=200)
        except Exception as e:
            return JsonResponse({
                "status": 500,
                "message": str(e)
            }, status=500)
    
class UpdateUserView(GenericAPIView):
    def put(self, request, userId):
        try:
            user = get_object_or_404(User, id=userId)
            serializer = UpdateUserSerializer(user, data=request.data, partial=True)
        
            if serializer.is_valid():
                serializer.save()
                
                # Sau khi update, dùng UserSerializer để lấy toàn bộ dữ liệu User
                full_user_data = FullInfoUserSerializer(user).data

                return JsonResponse({
                    "status": 200,
                    "message": "Updated user successfully",
                    "user": full_user_data  # Trả về toàn bộ dữ liệu User
                }, safe=False, status=200)
            
            return JsonResponse({
                "status": 400,
                "message": serializer.errors
            }, safe=False, status=400)
        except Exception as e:
            return JsonResponse({
                "status": 500,
                "message": str(e)
            }, status=500)
    
class DeleteUserView(GenericAPIView):
    permission_classes = [IsAdminUser]
    
    def delete(self, request, userId):
        try:
            user = get_object_or_404(User, id=userId)
            user.delete()
        
            return JsonResponse({
                    "status": 200,
                    "message": "Deleted user successfully",
            }, status=200)
        except Exception as e:
            return JsonResponse({
                "status": 500,
                "message": str(e)
            }, status=500)

class getAllUsersongView(GenericAPIView):
    # permission_classes = [IsAdminUser]

    def get(self, request, userId):
        try:
            user = get_object_or_404(User, id=userId)
            serializer = FullInfoUserSerializer(user, many=True)
        
            return JsonResponse({
                "status": 200,
                "message": "Updated user successfully",
                "user": serializer.data
            }, status=200)
        except Exception as e:
            return JsonResponse({
                "status": 500,
                "message": str(e)
            }, status=500)
    
class RequireUpdateUserToArtistView(GenericAPIView):
    def put(self, request, userId):
        try:
            user = get_object_or_404(User, id=userId)
            serializer = RequireUpdateUserToArtistSerializer(user, data=request.data)
        
            if serializer.is_valid():
                serializer.save()

                return JsonResponse({
                    "status": 200,
                    "message": "Required update user to artist successfully",
                    # "user": serializer.data
                }, status=200)
            
            return JsonResponse({
                "status": 400,
                "message": {serializer.errors}
            }, status=400)
        except Exception as e:
            return JsonResponse({
                "status": 500,
                "message": str(e)
            }, status=500)
        
class ResponseUpdateUserToArtistView(GenericAPIView):
    permission_classes = [IsAdminUser]
    
    def put(self, request, userId):
        try:
            user = get_object_or_404(User, id=userId)
            serializer = ResponseUpdateUserToArtistSerializer(user, data=request.data)
        
            if serializer.is_valid():
                serializer.save()

                return JsonResponse({
                    "status": 200,
                    "message": "Responsed update user to artist successfully",
                    # "user": serializer.data
                }, status=200)
            
            return JsonResponse({
                "status": 400,
                "message": {serializer.errors}
            }, status=400)
        except Exception as e:
            return JsonResponse({
                "status": 500,
                "message": str(e)
            }, status=500)