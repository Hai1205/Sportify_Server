from rest_framework.permissions import AllowAny, IsAdminUser
from Sportify_Server.permissions import IsArtistUser
from rest_framework.generics import GenericAPIView
from Sportify_Server.services import AwsS3Service
from .serializers import FullInfoAlbumSerializer
from .models import Song
from albums.models import Album
from users.models import User
from django.shortcuts import get_object_or_404
from django.http import JsonResponse

class uploadSongView(GenericAPIView):
    permission_classes = [ IsAdminUser or IsArtistUser]

    def get_audio_duration(self, audioUrl):
        import requests
        from mutagen.mp3 import MP3
        from io import BytesIO
        """Lấy thời lượng của file MP3"""
        response = requests.get(audioUrl)
        if response.status_code == 200:
            audio = MP3(BytesIO(response.content))  # Đọc file MP3 từ memory
            return audio.info.length  # Thời lượng tính bằng giây
        return None
        
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
            thumbnail = request.FILES.get("thumbnail")
            audio = request.FILES.get("audio")
            # duration = int(request.data.get("duration"))
            
            if thumbnail is None or audio is None:
                return JsonResponse({
                    "status": 400,
                    "message": "Please upload thumbnail and audio"
                }, status=400)
            
            s3_service = AwsS3Service()
            thumbnailUrl = s3_service.save_file_to_s3(thumbnail)
            audioUrl = s3_service.save_file_to_s3(audio)
            
            duration = self.get_audio_duration(audioUrl)
            # Tạo bài hát mới
            song = Song.objects.create(
                user=user,
                album=album or None,
                title=title,
                thumbnailUrl=thumbnailUrl,
                audioUrl=audioUrl,
                duration=duration,
            )
            
            if album:
                album.songs.add(song)
                album.save()

            # Trả về response
            serializer = FullInfoAlbumSerializer(song)
           
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
            serializer = FullInfoAlbumSerializer(songs, many=True)
        
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
            serializer = FullInfoAlbumSerializer(song)
        
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
           
            albumId = song.album_id
            album = get_object_or_404(Album, id=albumId)
            album.songs.remove(song)
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
            serializer = FullInfoAlbumSerializer(songs, many=True)
            
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
            serializer = FullInfoAlbumSerializer(songs, many=True)
           
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
            serializer = FullInfoAlbumSerializer(songs, many=True)
          
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