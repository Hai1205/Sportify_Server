from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from .serializers import AlbumSerializer
from rest_framework.generics import GenericAPIView
from .models import Album
from Sportify_server.aws_s3_service import AwsS3Service
from django.shortcuts import get_object_or_404

class CreateAlbumView(GenericAPIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        title = request.data.get("title")
        description = request.data.get("description")
        thumbnail = request.FILES.get("thumbnail")
        
        if not thumbnail:
            return Response({"message": "Thumbnail is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        s3_service = AwsS3Service()
        thumbnailUrl = s3_service.save_file_to_s3(thumbnail)
        
        album = Album.objects.create(
            title=title,
            description=description,
            thumbnail_url=thumbnailUrl
        )
        
        return Response({
            "message": "Album created successfully",
            "album": AlbumSerializer(album).data
        }, status=status.HTTP_201_CREATED)
    
class GetAllAlbumView(GenericAPIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        songs = Album.objects.all()
        serializer = AlbumSerializer(songs, many=True)
       
        return Response(serializer.data)
    
class GetAllSongByAlbumIdView(GenericAPIView):
    permission_classes = [IsAdminUser]

    def get(self, request, albumId):
        try:
            album = get_object_or_404(Album, id=albumId)
            serializer = AlbumSerializer(album)
        
            return Response(serializer.data, status=status.HTTP_200_OK) 
        except Album.DoesNotExist:
            return Response({"message": "Album not found"}, status=status.HTTP_404_NOT_FOUND)

class DeleteAlbumByIdView(GenericAPIView):
    permission_classes = [IsAdminUser]
    
    def delete(self, request, albumId):
        album = get_object_or_404(Album, id=albumId)
        album.delete()
       
        return Response({"message": "Deleted successfully"}, status=status.HTTP_204_NO_CONTENT)