from rest_framework.permissions import AllowAny, IsAdminUser
from Sportify_Server.permissions import IsArtistUser
from .serializers import FullInfoAlbumSerializer
from rest_framework.generics import GenericAPIView
from .models import Album
from songs.models import Song
from users.models import User
from Sportify_Server.services import AwsS3Service
from django.shortcuts import get_object_or_404
from django.http import JsonResponse

class UploadAlbumView(GenericAPIView):
    permission_classes = [IsAdminUser | IsArtistUser ]

    def post(self, request, userId):
        try:
            user = get_object_or_404(User, id=userId)
            
            title = request.data.get("title")
            releaseDate = request.data.get("releaseDate")
            thumbnail = request.FILES.get("thumbnail")
            
            if thumbnail is None:
                return JsonResponse({
                    "status": 400,
                    "message": "Thumbnail is required"
                    }, status=400)
            
            s3_service = AwsS3Service()
            thumbnailUrl = s3_service.save_file_to_s3(thumbnail)
            
            album = Album.objects.create(
                user=user,
                title=title,
                releaseDate=releaseDate,
                thumbnailUrl=thumbnailUrl
            )
            
            if user:
                user.albums.add(album)
                user.save()
            
            return JsonResponse({
                "status": 200,
                "message": "Created album successfully",
                "album": FullInfoAlbumSerializer(album).data
            }, safe=False, status=200)
        except Exception as e:
            return JsonResponse({
                "status": 500,
                "message": str(e)
            }, status=500)
    
class GetAllAlbumView(GenericAPIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        try:
            albums = Album.objects.all()
            serializer = FullInfoAlbumSerializer(albums, many=True)
        
            return JsonResponse({
                "status": 200,
                "message": "Get all album successfully",
                "albums": serializer.data
            }, safe=False, status=200)
        except Exception as e:
            return JsonResponse({
                "status": 500,
                "message": str(e)
            }, status=500)
            
class GetUserAlbums(GenericAPIView):
    def get(self, request, userId):
        try:
            user = get_object_or_404(User, id=userId)
            albums = user.user_albums.all()
            
            serializer = FullInfoAlbumSerializer(albums, many=True)
        
            return JsonResponse({
                "status": 200,
                "message": "Get user albums successfully",
                "albums": serializer.data
            }, safe=False, status=200)
        except Exception as e:
            return JsonResponse({
                "status": 500,
                "message": str(e)
            }, status=500)
    
class GetAlbumView(GenericAPIView):
    permission_classes = [AllowAny]
    
    def get(self, request, albumId):
        try:
            album = get_object_or_404(Album, id=albumId)
            serializer = FullInfoAlbumSerializer(album)
        
            return JsonResponse({
                "status": 200,
                "message": "Get album successfully",
                "album": serializer.data
            }, safe=False, status=200)
        except Album.DoesNotExist:
            return JsonResponse({
                "status": 404,
                "message": "Album not found"
            }, status=404)
        except Exception as e:
            return JsonResponse({
                "status": 500,
                "message": str(e)
            }, status=500)

class DeleteAlbumView(GenericAPIView):
    permission_classes = [IsAdminUser | IsArtistUser ]
    
    def delete(self, request, albumId):
        try:
            album = get_object_or_404(Album, id=albumId)
            
            Song.objects.filter(album_id=albumId).delete()
            
            album.delete()
        
            return JsonResponse({
                "status": 200,
                "message": "Deleted album successfully",
            }, status=200)
        except Exception as e:
            return JsonResponse({
                "status": 500,
                "message": str(e)
            }, status=500)