from rest_framework.permissions import IsAdminUser
from Sportify_Server.permissions import IsArtistUser, HasAnyPermission
from .serializers import AlbumSerializer
from rest_framework.generics import GenericAPIView
from .models import Album
from songs.models import Song
from Sportify_Server.services import AwsS3Service
from django.shortcuts import get_object_or_404
from django.http import JsonResponse

class CreateAlbumView(GenericAPIView):
    permission_classes = [HasAnyPermission(IsArtistUser, IsAdminUser)]

    def post(self, request, userId):
        try:
            title = request.data.get("title")
            releaseDate = request.data.get("releaseDate")
            # description = request.data.get("description")
            thumbnail = request.FILES.get("thumbnail")
            
            if thumbnail is None:
                return JsonResponse({"message": "Thumbnail is required"}, status=400)
            
            s3_service = AwsS3Service()
            thumbnailUrl = s3_service.save_file_to_s3(thumbnail)
            
            album = Album.objects.create(
                userId=userId,
                title=title,
                releaseDate=releaseDate,
                # description=description,
                thumbnail_url=thumbnailUrl
            )
            
            return JsonResponse({
                "message": "Album created successfully",
                "album": AlbumSerializer(album).data
            }, safe=False, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    
class GetAllAlbumView(GenericAPIView):
    def get(self, request):
        try:
            songs = Album.objects.all()
            serializer = AlbumSerializer(songs, many=True)
        
            return JsonResponse(serializer.data, safe=False, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    
class GetAllSongByAlbumIdView(GenericAPIView):
    def get(self, request, albumId):
        try:
            album = get_object_or_404(Album, id=albumId)
            serializer = AlbumSerializer(album)
        
            return JsonResponse(serializer.data, safe=False, status=200) 
        except Album.DoesNotExist:
            return JsonResponse({"message": "Album not found"}, status=404)

class DeleteAlbumByIdView(GenericAPIView):
    permission_classes = [HasAnyPermission(IsArtistUser, IsAdminUser)]
    
    def delete(self, request, albumId):
        try:
            album = get_object_or_404(Album, id=albumId)
            
            Song.objects.filter(albumId=albumId).delete()
            
            album.delete()
        
            return JsonResponse({"message": "Deleted successfully"}, safe=False, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)