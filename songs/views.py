from rest_framework.permissions import AllowAny, IsAdminUser
from Sportify_Server.permissions import IsArtistUser
from rest_framework.generics import GenericAPIView
from Sportify_Server.services import AwsS3Service
from .serializers import FullInfoSongSerializer, SongSerializer
from .models import Song
from albums.models import Album
from users.models import User
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
import requests
from mutagen.mp3 import MP3
from io import BytesIO
from django.db.models import Q

class uploadSongView(GenericAPIView):
    permission_classes = [IsAdminUser or IsArtistUser]

    def get_audio_duration(self, audioUrl):
        """Lấy thời lượng của file MP3"""
        response = requests.get(audioUrl)
        if response.status_code == 200:
            audio = MP3(BytesIO(response.content))  # Đọc file MP3 từ memory
            return audio.info.length  # Thời lượng tính bằng giây
        return None
        
    def post(self, request, userId):
        # print(userId)
        try:
            # Kiểm tra id có tồn tại không
            album = None
            user = get_object_or_404(User, id=userId)
            
            # Lấy dữ liệu từ request
            title = request.data.get("title")
            thumbnail = request.FILES.get("thumbnail")
            audio = request.FILES.get("audio")
            genre = request.data.get("genre")
            lyric = request.data.get("lyric")
            releaseDate = request.data.get("releaseDate")
            albumId = request.data.get("albumId")
            
            if albumId:
                album = get_object_or_404(Album, id=albumId)
            
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
                lyric=lyric,
                genre=genre,
                releaseDate=releaseDate,
            )
            
            user.songs.add(song)
            user.save()
            
            if album:
                album.songs.add(song)
                album.save()

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
            
            serializer = FullInfoSongSerializer(songs, many=True)
        
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
            
            serializer = FullInfoSongSerializer(song)
        
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
    permission_classes = [IsAdminUser | IsArtistUser]
    
    def delete(self, request, songId):
        try:
            song = get_object_or_404(Song, id=songId)
           
            albumId = song.album_id
            album = get_object_or_404(Album, id=albumId)
            album.songs.remove(song)
            album.save()
            
            userId = song.user_id
            user = get_object_or_404(User, id=userId)
            user.songs.remove(song)
            user.save()
            
            thumbnailUrl = user.thumbnailUrl
            audioUrl = user.audioUrl
            s3_service = AwsS3Service()
            s3_service.delete_file_from_s3(thumbnailUrl)
            s3_service.delete_file_from_s3(audioUrl)
    
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
            songLimit = 6
            songs = Song.objects.order_by("?")[:songLimit]
            
            serializer = FullInfoSongSerializer(songs, many=True)
            
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
            songLimit = 4
            songs = Song.objects.order_by("?")[:songLimit]
            
            serializer = FullInfoSongSerializer(songs, many=True)
           
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
            songLimit = 4
            songs = Song.objects.order_by("?")[:songLimit]
            
            serializer = FullInfoSongSerializer(songs, many=True)
          
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

class UpdateSongView(GenericAPIView):
    permission_classes = [IsAdminUser | IsArtistUser]
    
    def put(self, request, songId):
        try:
            song = get_object_or_404(Song, id=songId)
            
            # songwriter = request.FILES.get("songwriter")
            # producer = request.FILES.get("producer")
            albumId = request.data.get("albumId")
            title = request.data.get("title")
            thumbnail = request.FILES.get("thumbnail")
            genre = request.data.get("genre")
            releaseDate = request.data.get("releaseDate")
            
            if albumId is not None:
                album = get_object_or_404(Album, id=albumId)
                song.album = album
            
            # song.producer = producer
            # song.songwriter = songwriter
            song.releaseDate = releaseDate
            song.genre = genre
            song.title = title
            if thumbnail is not None:
                s3_service = AwsS3Service()
                thumbnailUrl = s3_service.save_file_to_s3(thumbnail)
                song.thumbnailUrl = thumbnailUrl
            
            song.save()
            
            serializer = FullInfoSongSerializer(song)
            
            return JsonResponse({
                "songs": 200,
                "message": "Updated song successfully", 
                "song": serializer.data
            }, safe=False, status=200)
        except Exception as e:
            return JsonResponse({
                "status": 500,
                "message": str(e)
            }, status=500)

class AddSongToAlbumView(GenericAPIView):
    permission_classes = [IsAdminUser | IsArtistUser]
    
    def put(self, request, songId, albumId):
        try:
            song = get_object_or_404(Song, id=songId)
            
            album = get_object_or_404(Album, id=albumId)
            album.songs.add(song)
            album.save()
            
            song.album = album
            song.save()
            
            serializer = FullInfoSongSerializer(song)
            
            return JsonResponse({
                "songs": 200,
                "message": "Add song to album successfully",
                "song": serializer.data 
            }, safe=False, status=200)
        except Exception as e:
            return JsonResponse({
                "status": 500,
                "message": str(e)
            }, status=500)

class DownloadSongView(GenericAPIView):
    permission_classes = [AllowAny]
    
    def get(self, request, songId):
        try:
            song = get_object_or_404(Song, id=songId)
            
            audioUrl = song.audioUrl
            title = song.title
            print(title)
            
            s3_service = AwsS3Service()
            s3_service.download_file_from_s3("https://sportify-clone.s3.amazonaws.com/c842ecc4-12cc-467b-b10c-eb8174ee5f27.mp3", title)
          
            return JsonResponse({
                "songs": 200,
                "message": "Download song successfully", 
            }, safe=False, status=200)
        except Exception as e:
            return JsonResponse({
                "status": 500,
                "message": str(e)
            }, status=500)

class SearchSongsView(GenericAPIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        try:
            query = request.GET.get('query')
            
            songs = Song.objects.filter(Q(title__icontains=query) | Q(user__fullName__icontains=query) | Q(album__title__icontains=query))
                      
            serializer = FullInfoSongSerializer(songs, many=True)
            
            return JsonResponse({
                "songs": 200,
                "message": "Search songs successfully", 
                "songs": serializer.data
            }, safe=False, status=200)
        except Exception as e:
            return JsonResponse({
                "status": 500,
                "message": str(e)
            }, status=500)

class IncreaseSongViewView(GenericAPIView):
    permission_classes = [AllowAny]

    def put(self, request, songId):
        try:
            song = get_object_or_404(Song, id=songId)
            song.views += 1
            song.save(update_fields=['views'])

            serializer = FullInfoSongSerializer(song)
            
            return JsonResponse({
                "status": 200,
                "message": "Increase song view successfully",
                "song": serializer.data
            })
        except Exception as e:
            return JsonResponse({
                "status": 500,
                "message": str(e)
            })