from rest_framework.permissions import IsAdminUser
from .serializers import SongSerializer
from rest_framework.generics import GenericAPIView
from .models import Song
from albums.models import Album
from users.models import User
from Sportify_Server.services import AwsS3Service
from Sportify_Server.permissions import IsArtistUser, HasAnyPermission
from django.shortcuts import get_object_or_404
from django.http import JsonResponse

class AddSongView(GenericAPIView):
    permission_classes = [IsArtistUser or IsAdminUser]

    def post(self, request, userId, albumId):
        try:
            if thumbnail is None or audioUrl is None:
                return JsonResponse({"message": "Please upload thumbnail and audio"}, status=400)
            
            # Lấy dữ liệu từ request
            title = request.data.get("title")
            # description = request.data.get("description")
            thumbnail = request.FILES.get("thumbnail")
            audio = request.FILES.get("audio")
            duration = request.FILES.get("duration")
            
            # Kiểm tra id có tồn tại không
            album = None
            if albumId:
                album = get_object_or_404(Album, id=albumId)
            get_object_or_404(User, id=userId)
                
            s3_service = AwsS3Service()
            thumbnailUrl = s3_service.save_file_to_s3(thumbnail)
            audioUrl = s3_service.save_file_to_s3(audio)

            # Tạo bài hát mới
            song = Song.objects.create(
                userId=userId,
                albumId=albumId or None,
                title=title,
                # description=description,
                thumbnail_url=thumbnailUrl,
                audioUrl=audioUrl,
                duration=duration,
            )
            
            if album:
                album.songs.append(str(song.id))
                album.save()

            # Trả về response
            serializer = SongSerializer(song)
           
            return JsonResponse({"message": "Song Added", "song": serializer.data}, safe=False, status=200)
        except Exception as e:
            raise Exception(f"Unexpected error: {str(e)}")
        
class GetAllSongView(GenericAPIView):
    def get(self, request):
        try:
            songs = Song.objects.all()
            serializer = SongSerializer(songs, many=True)
        
            return JsonResponse(serializer.data, safe=False, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    
class GetSongByIdView(GenericAPIView):
    def get(self, request, songId):
        try:
            song = get_object_or_404(Song, id=songId)
            serializer = SongSerializer(song)
        
            return JsonResponse(serializer.data, safe=False, status=200) 
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

class DeleteSongByIdView(GenericAPIView):
    permission_classes = [HasAnyPermission(IsArtistUser, IsAdminUser)]
    
    def delete(self, request, songId):
        try:
            song = get_object_or_404(Song, id=songId)
            album = get_object_or_404(Album, id=song.albumId)
            
            album.songs.remove(songId)
            album.save()
    
            song.delete()
        
            return JsonResponse({"message": "Deleted successfully"}, safe=False, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    
class GetFeaturedView(GenericAPIView):
    def get(self, request):
        try:
            random = 6
            songs = Song.objects.order_by("?")[:random].values("id", "title", "userID", "imageUrl", "audioUrl")
            serializer = SongSerializer(songs, many=True)
            
            return JsonResponse(serializer.data, safe=False, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    
class GetTrendingView(GenericAPIView):
    def get(self, request):
        try:
            random = 4
            songs = Song.objects.order_by("?")[:random].values("id", "title", "userID", "imageUrl", "audioUrl")
            serializer = SongSerializer(songs, many=True)
           
            return JsonResponse(serializer.data, safe=False, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    
class GetMadeForYouView(GenericAPIView):
    def get(self, request):
        try:
            random = 4
            songs = Song.objects.order_by("?")[:random].values("id", "title", "userID", "imageUrl", "audioUrl")
            serializer = SongSerializer(songs, many=True)
          
            return JsonResponse(serializer.data, safe=False, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)