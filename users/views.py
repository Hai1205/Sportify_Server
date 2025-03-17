from rest_framework.permissions import IsAdminUser, AllowAny
from .serializers import UserSerializer, \
                            FullInfoUserSerializer, \
                            ResponseUpdateUserToArtistSerializer, \
                            FullInfoArtistApplicationSerializer
                            # UpdateUserSerializer, \
from .models import User, ArtistApplication
from songs.models import Song
from rest_framework.generics import GenericAPIView
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.db.models import Q
import requests
from mutagen.mp3 import MP3
from io import BytesIO
from Sportify_Server.services import AwsS3Service

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
            
            data = request.data
            avatar = request.FILES.get("avatar")
            
            if 'fullName' in data:
                user.fullName = data['fullName']
            if 'country' in data:
                user.country = data['country']
            if 'biography' in data:
                user.biography = data['biography']
            if 'role' in data:
                user.role = data['role']
            if 'status' in data:
                user.status = data['status']
            
            if avatar is not None:
                s3_service = AwsS3Service()
                avatarUrl = s3_service.save_file_to_s3(avatar)
                user.avatarUrl = avatarUrl

            user.save()
            
            serializer = FullInfoUserSerializer(user)
            return JsonResponse({
                "status": 200,
                "message": "Updated user successfully",
                "user": serializer.data
            }, safe=False, status=200)
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
            
            avatarUrl = user.avatarUrl
            s3_service = AwsS3Service()
            s3_service.delete_file_from_s3(avatarUrl)
            
            songs = Song.objects.filter(user_id=userId)
            for song in songs:
                s3_service.delete_file_from_s3(song.thumbnailUrl)
                s3_service.delete_file_from_s3(song.audioUrl)
                song.delete()
            
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

class getAllUserSongsView(GenericAPIView):
    permission_classes = [AllowAny]
    
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
    def get_audio_duration(self, audioUrl):
        """Lấy thời lượng của file MP3"""
        response = requests.get(audioUrl)
        if response.status_code == 200:
            audio = MP3(BytesIO(response.content))  # Đọc file MP3 từ memory
            return audio.info.length  # Thời lượng tính bằng giây
        return None
    
    def post(self, request, userId):
        try:
            isAgree = request.data.get("isAgree")
            if not isAgree:
                return JsonResponse({
                    "status": 400,
                    "message": "You must agree to the Artist Terms and Conditions"
                }, status=400)
            
            user = get_object_or_404(User, id=userId)
            
            primaryGenre = request.data.get("primaryGenre")
            secondaryGenre = request.data.get("secondaryGenre")
            biography = request.data.get("biography")
            achievements = request.data.get("achievements")
            
            website = request.data.get("website")
            instagram = request.data.get("instagram")
            twitter = request.data.get("twitter")
            facebook = request.data.get("facebook")
            youtube = request.data.get("youtube")
           
            song1Title = request.data.get("song1Title")
            song1Audio = request.data.get("song1Audio")
           
            song2Title = request.data.get("song2Title")
            song2Audio = request.data.get("song2Audio")
           
            song3Title = request.data.get("song3Title")
            song3Audio = request.data.get("song3Audio")
           
            reason = request.data.get("reason")
            
            s3_service = AwsS3Service()
            song1AudioUrl = s3_service.save_file_to_s3(song1Audio)
            song2AudioUrl = s3_service.save_file_to_s3(song2Audio)
            song3AudioUrl = s3_service.save_file_to_s3(song3Audio)
            
            song1Duration = self.get_audio_duration(song1AudioUrl)
            song2Duration = self.get_audio_duration(song2AudioUrl)
            song3Duration = self.get_audio_duration(song3AudioUrl)
            
            artistApplication = ArtistApplication.objects.create(
                user=user,
                primaryGenre=primaryGenre,
                secondaryGenre=secondaryGenre,
                biography=biography,
                achievements=achievements,
                website=website,
                instagram=instagram,
                twitter=twitter,
                facebook=facebook,
                youtube=youtube,
                reason=reason,
            )
            
            song1 = Song.objects.create(
                user=user,
                title=song1Title,
                audioUrl=song1AudioUrl,
                duration=song1Duration,
            )
            
            song2 = Song.objects.create(
                user=user,
                title=song2Title,
                audioUrl=song2AudioUrl,
                duration=song2Duration,
            )
            
            song3 = Song.objects.create(
                user=user,
                title=song3Title,
                audioUrl=song3AudioUrl,
                duration=song3Duration,
            )
            
            artistApplication.songs.set([song1, song2, song3])

            return JsonResponse({
                "status": 200,
                "message": "Required update user to artist successfully",
            }, status=200)
        except Exception as e:
            return JsonResponse({
                "status": 500,
                "message": str(e)
            }, status=500)
        
class ResponseUpdateUserToArtistView(GenericAPIView):
    permission_classes = [IsAdminUser]
    
    def put(self, request, applicationId):
        try:
            application = get_object_or_404(ArtistApplication, id=applicationId)
            
            serializer = ResponseUpdateUserToArtistSerializer(application, data=request.data)
        
            if serializer.is_valid():
                serializer.save()

                return JsonResponse({
                    "status": 200,
                    "message": "Responsed update user to artist successfully",
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
            
class SearchUsersView(GenericAPIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        try:
            query = request.GET.get('query')
            
            users = User.objects.filter(Q(fullName__icontains=query) | Q(username__icontains=query) | Q(email__icontains=query))
            
            serializer = FullInfoUserSerializer(users, many=True)
            
            return JsonResponse({
                "users": 200,
                "message": "Search users successfully", 
                "users": serializer.data
            }, safe=False, status=200)
        except Exception as e:
            return JsonResponse({
                "status": 500,
                "message": str(e)
            }, status=500)
            
class GetArtistApplications(GenericAPIView):
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        try:
            status = request.GET.get('status')
            print(1)
            artistApplications = ArtistApplication.objects.filter(Q(status__icontains=status))
            print(2)
            serializer = FullInfoArtistApplicationSerializer(artistApplications, many=True)
            print(3)
            return JsonResponse({
                "status": 200,
                "message": f"Get {status} artist applications successfully",
                "artistApplications": serializer.data
            }, safe=False, status=200)
        except Exception as e:
            return JsonResponse({
                "status": 500,
                "message": str(e)
            }, status=500)
            
class DeleteArtistApplicationView(GenericAPIView):
    permission_classes = [IsAdminUser]
    
    def delete(self, request, applicationId):
        try:
            application = get_object_or_404(ArtistApplication, id=applicationId)

            s3_service = AwsS3Service()
            userId = application.user
            songs = Song.objects.filter(user_id=userId)
            for song in songs:
                s3_service.delete_file_from_s3(song.audioUrl)
                song.delete()
            
            application.delete()
        
            return JsonResponse({
                    "status": 200,
                    "message": "Deleted artist application successfully",
            }, status=200)
        except Exception as e:
            return JsonResponse({
                "status": 500,
                "message": str(e)
            }, status=500)