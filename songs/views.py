from rest_framework.permissions import AllowAny, IsAdminUser
from Sportify_Server.permissions import IsArtistUser
from rest_framework.generics import GenericAPIView
from Sportify_Server.services import AwsS3Service
from .serializers import SongSerializer
from .models import Song
from albums.models import Album
from users.models import User
from django.shortcuts import get_object_or_404
from django.http import JsonResponse

class uploadSongView(GenericAPIView):
    permission_classes = [ IsAdminUser or IsArtistUser]

    def post(self, request, userId, albumId):
        # print(userId)
        try:
            # Kiểm tra id có tồn tại không
            album = None
            if albumId:
                album = get_object_or_404(Album, id=albumId)
            user = get_object_or_404(User, id=userId)
            
            # Lấy dữ liệu từ request
            title = request.data.get("title")
            # description = request.data.get("description")
            thumbnail = request.FILES.get("thumbnail")
            audio = request.FILES.get("audio")
            duration = int(request.data.get("duration"))
            
            if thumbnail is None or audio is None:
                return JsonResponse({
                    "status": 400,
                    "message": "Please upload thumbnail and audio"
                }, status=400)
            
            s3_service = AwsS3Service()
            thumbnailUrl = s3_service.save_file_to_s3(thumbnail)
            audioUrl = s3_service.save_file_to_s3(audio)

            # Tạo bài hát mới
            song = Song.objects.create(
                userId=user,
                albumId=album or None,
                title=title,
                # description=description,
                thumbnailUrl=thumbnailUrl,
                audioUrl=audioUrl,
                duration=duration,
            )
            
            if album:
                album.songs.add(song)
                album.save()

            # Trả về response
            serializer = SongSerializer(song)
           
            return JsonResponse({
                "songs": 200,
                "message": "Added song successfully", 
                "song": serializer.data
            }, safe=False, status=200)
        except Exception as e:
            raise Exception(f"Unexpected error: {str(e)}")
        
class GetAllSongView(GenericAPIView):
    def get(self, request):
        try:
            songs = Song.objects.all()
            serializer = SongSerializer(songs, many=True)
        
            return JsonResponse({
                "songs": 200,
                "message": "Get all song successfully", 
                "songs": serializer.data
            }, safe=False, status=200)
        except Exception as e:
            return JsonResponse({
                "status": 500,
                "message": str(e)
            }, status=500)
    
class GetSongView(GenericAPIView):
    def get(self, request, songId):
        try:
            song = get_object_or_404(Song, id=songId)
            serializer = SongSerializer(song)
        
            return JsonResponse({
                "songs": 200,
                "message": "Get song successfully", 
                "song": serializer.data
            }, safe=False, status=200)
        except Exception as e:
            return JsonResponse({
                "status": 500,
                "message": str(e)
            }, status=500)

class DeleteSongView(GenericAPIView):
    permission_classes = [IsAdminUser | IsArtistUser ]
    
    def delete(self, request, songId):
        try:
            song = get_object_or_404(Song, id=songId)
           
            albumId = song.albumId_id
            album = get_object_or_404(Album, id=albumId)
            album.songs.remove(songId)
            album.save()
    
            song.delete()
        
            return JsonResponse({
                "status": 200,
                "message": "Deleted song successfully"
            }, status=200)
        except Exception as e:
            return JsonResponse({
                "status": 500,
                "message": str(e)
            }, status=500)
    
class GetFeaturedView(GenericAPIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        try:
            element = 6
            songs = Song.objects.order_by("?")[:element]
            serializer = SongSerializer(songs, many=True)
            
            return JsonResponse({
                "songs": 200,
                "message": "Get song featured songs successfully", 
                "songs": serializer.data
            }, safe=False, status=200)
        except Exception as e:
            return JsonResponse({
                "status": 500,
                "message": str(e)
            }, status=500)
    
class GetTrendingView(GenericAPIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        try:
            element = 4
            songs = Song.objects.order_by("?")[:element]
            serializer = SongSerializer(songs, many=True)
           
            return JsonResponse({
                "songs": 200,
                "message": "Get trending songs successfully", 
                "songs": serializer.data
            }, safe=False, status=200)
        except Exception as e:
            return JsonResponse({
                "status": 500,
                "message": str(e)
            }, status=500)
    
class GetMadeForYouView(GenericAPIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        try:
            element = 4
            songs = Song.objects.order_by("?")[:element]
            serializer = SongSerializer(songs, many=True)
          
            return JsonResponse({
                "songs": 200,
                "message": "Get made for you songs successfully", 
                "songs": serializer.data
            }, safe=False, status=200)
        except Exception as e:
            return JsonResponse({
                "status": 500,
                "message": str(e)
            }, status=500)