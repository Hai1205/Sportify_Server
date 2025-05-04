from rest_framework.permissions import AllowAny, IsAdminUser
from Sportify_server.permissions import IsArtistUser
from rest_framework.generics import GenericAPIView
from Sportify_server.services import AwsS3Service
from .serializers import *
from users.serializers import *
from .models import Song
from Sportify_server.services import AwsS3Service
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
import requests
from mutagen.mp3 import MP3
from io import BytesIO
from django.db.models import Q
from rest_framework.views import APIView
from django.db import connection
from albums.models import Album

class uploadSongView(GenericAPIView):
    permission_classes = [IsAdminUser or IsArtistUser]

    def get_audio_duration(self, audioUrl):
        response = requests.get(audioUrl)
        
        if response.status_code == 200:
            audio = MP3(BytesIO(response.content))
            return audio.info.length
        return None

    def post(self, request, userId):
        try:
            album = None
            user = get_object_or_404(User, id=userId)

            title = request.data.get("title")
            thumbnail = request.FILES.get("thumbnail")
            audio = request.FILES.get("audio")
            video = request.FILES.get("video")
            lyrics = request.data.get("lyrics")
            albumId = request.data.get("albumId")

            if albumId and albumId != "none":
                album = get_object_or_404(Album, id=albumId)

            if thumbnail is None or audio is None or video is None:
                return JsonResponse({
                    "status": 400,
                    "message": "Please upload thumbnail video and audio"
                }, status=400)

            s3_service = AwsS3Service()
            thumbnailUrl = s3_service.save_file_to_s3(thumbnail)
            audioUrl = s3_service.save_file_to_s3(audio)
            videoUrl = s3_service.save_file_to_s3(video)

            duration = self.get_audio_duration(audioUrl)

            song = Song.objects.create(
                title=title,
                thumbnailUrl=thumbnailUrl,
                audioUrl=audioUrl,
                videoUrl=videoUrl,
                duration=duration,
                lyrics=lyrics,
            )

            user.songs.add(song)
            user.save()

            if album:
                album.songs.add(song)
                album.save()

            serializer = FullInfoSongSerializer(song)

            return JsonResponse({
                "status": 200,
                "message": "Added song successfully",
                "song": serializer.data
            }, safe=False, status=200)
        except Exception as e:
            return JsonResponse({"status": 500, "message": f"Unexpected error: {str(e)}"}, status=500)
        
class GetAllSongView(GenericAPIView):
    permission_classes = [AllowAny]
    
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
    permission_classes = [AllowAny]

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
    # permission_classes = [IsAdminUser | IsArtistUser]
    def get_audio_duration(self, audioUrl):
        response = requests.get(audioUrl)
        
        if response.status_code == 200:
            audio = MP3(BytesIO(response.content))
            return audio.info.length
        return None
    
    def put(self, request, songId):
        try:
            song = get_object_or_404(Song, id=songId)
            
            albumId = request.data.get("albumId")
            thumbnail = request.FILES.get("thumbnail")
            audio = request.FILES.get("audio")
            video = request.FILES.get("video")
            title = request.data.get("title")
            lyrics = request.data.get("lyrics")
            
            album = Album.objects.filter(songs=song).first()
            if albumId == "none" and album:
                album.songs.remove(song)
            elif albumId and albumId != "none":
                if album:
                    album.songs.remove(song)
                album = get_object_or_404(Album, id=albumId)
                album.songs.add(song)
            
            song.title = title
            song.lyrics = lyrics
            
            if thumbnail is not None:
                s3_service = AwsS3Service()
                thumbnailUrl = s3_service.save_file_to_s3(thumbnail)
                song.thumbnailUrl = thumbnailUrl
                
            if thumbnail is not None:
                s3_service = AwsS3Service()
                audioUrl = s3_service.save_file_to_s3(audio)
                song.audioUrl = audioUrl

            if video is not None:
                s3_service = AwsS3Service()
                videoUrl = s3_service.save_file_to_s3(video)
                song.videoUrl = videoUrl
            
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
            s3_service.download_file_from_s3(audioUrl, title)
          
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
            print(query)
            
            songs = Song.objects.filter(Q(title__icontains=query))
                      
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
            print("increase song view")
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

class LikeSongView(GenericAPIView):
    def post(self, request, userId, songId):
        try:
            user = get_object_or_404(User, id=userId)
            song = get_object_or_404(Song, id=songId)

            if song in user.likedSongs.all():
                user.likedSongs.remove(song)
                message = "unliked"
            else:
                user.likedSongs.add(song)
                message = "liked"

            user.save()
            
            serializer = FullInfoUserSerializer(user)

            return JsonResponse({
                "status": 200,
                "message": f"User {message} song successfully",
                "user": serializer.data
            }, status=200)

        except Exception as e:
            return JsonResponse({
                "status": 500,
                "message": str(e)
            }, status=500)
            
class GetUserLikedSongView(GenericAPIView):
    permission_classes = [AllowAny]

    def get(self, request, userId):
        try:
            user = get_object_or_404(User, id=userId)

            serializer = FullInfoSongSerializer(user.likedSongs, many=True)
        
            return JsonResponse({
                "songs": 200,
                "message": "Get user liked songs successfully", 
                "songs": serializer.data
            }, safe=False, status=200)
        except Exception as e:
            return JsonResponse({
                "status": 500,
                "message": str(e)
            }, status=500)
            
class GetUserSongs(GenericAPIView):
    def get(self, request, userId):
        try:
            user = get_object_or_404(User, id=userId)
            songs = user.songs.all()
            
            serializer = FullInfoSongSerializer(songs, many=True)
        
            return JsonResponse({
                "status": 200,
                "message": "Get user songs successfully",
                "songs": serializer.data
            }, safe=False, status=200)
        except Exception as e:
            return JsonResponse({
                "status": 500,
                "message": str(e)
            }, status=500)