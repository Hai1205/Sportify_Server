from rest_framework.permissions import IsAdminUser, AllowAny
from .serializers import *
from .models import *
from songs.models import Song
from rest_framework.generics import GenericAPIView
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.db.models import Q
import requests
from mutagen.mp3 import MP3
from io import BytesIO
from Sportify_server.services import *

class CreateUserView(GenericAPIView):
    permission_classes = [IsAdminUser] 

    def post(self, request):
        try:
            serializer = CreateUserSerializer(data=request.data)
            if serializer.is_valid():
                user = serializer.save()
                
                full_info_serializer = FullInfoUserSerializer(user)
                
                return JsonResponse({
                    "status": 200,
                    "message": "Create user successfully",
                    "user": full_info_serializer.data
                }, status=200)
            
            return JsonResponse({
                    "status": 400,
                    "message": "Username or email already exists"
                }, status=400)
        except Exception as e:
            return JsonResponse({
                "status": 500,
                "message": str(e)
            }, status=500)
            
class GetAllUserView(GenericAPIView):
    permission_classes = [AllowAny]

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
                currentUser.following.remove(opponent)
                opponent.followers.remove(currentUser)
                message = "unfollowed"
            else:
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
    permission_classes = [AllowAny]

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
            
            UPDATABLE_FIELDS = {
                'fullName', 'country', 'biography', 'role', 'status',
                'website', 'instagram', 'twitter', 'facebook', 'youtube'
            }
            
            for field in UPDATABLE_FIELDS:
                if field in request.data:
                    setattr(user, field, request.data[field])
            
            if avatar := request.FILES.get("avatar"):
                s3_service = AwsS3Service()
                user.avatarUrl = s3_service.save_file_to_s3(avatar)

            user.save()
            
            return JsonResponse({
                "status": 200,
                "message": "Updated user successfully",
                "user": FullInfoUserSerializer(user).data
            }, status=200)
            
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
            
            songs = user.songs.all()
            for song in songs:
                s3_service.delete_file_from_s3(song.thumbnailUrl)
                s3_service.delete_file_from_s3(song.audioUrl)
                s3_service.delete_file_from_s3(song.videoUrl)
                song.delete()
                
            albums = user.albums.all()
            for album in albums:
                s3_service.delete_file_from_s3(album.thumbnailUrl)
                album.delete()
            
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
        response = requests.get(audioUrl)
        if response.status_code == 200:
            audio = MP3(BytesIO(response.content)) 
            
            return audio.info.length 
        
        return None
    
    def post(self, request, userId):
        try:
            user = get_object_or_404(User, id=userId)
            
            achievements = request.data.get("achievements")
            
            song1Title = request.data.get("song1Title")
            song1Audio = request.data.get("song1Audio")
           
            song2Title = request.data.get("song2Title")
            song2Audio = request.data.get("song2Audio")
           
            song3Title = request.data.get("song3Title")
            song3Audio = request.data.get("song3Audio")
           
            reason = request.data.get("reason")
            
            if not (song1Title and song1Audio) and not (song2Title and song2Audio) and not (song3Title and song3Audio):
                return JsonResponse({
                    "status": 400,
                    "message": "At least one song title and audio must be provided."
                }, status=400)
                
            s3_service = AwsS3Service()
            song1AudioUrl = s3_service.save_file_to_s3(song1Audio)
            song2AudioUrl = s3_service.save_file_to_s3(song2Audio)
            song3AudioUrl = s3_service.save_file_to_s3(song3Audio)
            
            song1Duration = self.get_audio_duration(song1AudioUrl)
            song2Duration = self.get_audio_duration(song2AudioUrl)
            song3Duration = self.get_audio_duration(song3AudioUrl)
            
            artistApplication = ArtistApplication.objects.create(
                user=user,
                achievements=achievements,
                reason=reason,
            )
            
            song1 = Song.objects.create(
                title=song1Title,
                audioUrl=song1AudioUrl,
                duration=song1Duration,
            )
            
            song2 = Song.objects.create(
                title=song2Title,
                audioUrl=song2AudioUrl,
                duration=song2Duration,
            )
            
            song3 = Song.objects.create(
                title=song3Title,
                audioUrl=song3AudioUrl,
                duration=song3Duration,
            )
            
            user.songs.set([song1, song2, song3])
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

            serializer = ResponseUpdateUserToArtistSerializer(application, data=request.data, context={'request': request})
        
            if serializer.is_valid():
                serializer.save()

                return JsonResponse({
                    "status": 200,
                    "message": "Responded update user to artist successfully",
                    "application": serializer.data
                }, status=200)
            
            return JsonResponse({
                "status": 400,
                "message": serializer.errors
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
            query = request.GET.get('query', '').strip()
            status = request.GET.get('status', '').strip()
            role = request.GET.get('role', '').strip()
            isAdmin = request.GET.get('admin', '').lower() == 'true'
            
            filters = Q()

            if not isAdmin:
                filters &= Q(status="active")
                
                if query:
                    filters &= (
                        Q(fullName__icontains=query) | 
                        Q(username__icontains=query) | 
                        Q(email__icontains=query)
                    )
            else:
                if role:
                    role_list = role.split(',')
                    role_filters = Q()
                    for r in role_list:
                        role_filters |= Q(role=r.strip())
                    filters &= role_filters

                if status:
                    status_list = status.split(',')
                    status_filters = Q()
                    for s in status_list:
                        status_filters |= Q(status__icontains=s.strip())
                    filters &= status_filters

                if query:
                    filters &= (
                        Q(fullName__icontains=query) | 
                        Q(username__icontains=query) | 
                        Q(email__icontains=query)
                    )

            users = User.objects.filter(filters).distinct()
            serializer = FullInfoUserSerializer(users, many=True)

            return JsonResponse({
                "status": 200,
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

            if status:
                status_list = status.split(',')
                artistApplications = ArtistApplication.objects.filter(Q(status__in=status_list))
            else:
                artistApplications = ArtistApplication.objects.all()
            serializer = FullInfoArtistApplicationSerializer(artistApplications, many=True)

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
            
class GetArtistApplication(GenericAPIView):
    def get(self, request, userId):
        try:
            user = get_object_or_404(User, id=userId)
            artistApplication = ArtistApplication.objects.filter(Q(user=user)).first()
            serializer = FullInfoArtistApplicationSerializer(artistApplication)

            return JsonResponse({
                "status": 200,
                "message": "Get artist application successfully",
                "artistApplication": serializer.data
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