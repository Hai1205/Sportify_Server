from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from .serializers import SongSerializer
from rest_framework.generics import GenericAPIView
from .models import Song
from Sportify_server.aws_s3_service import AwsS3Service
from django.shortcuts import get_object_or_404

class AddSongView(GenericAPIView):
    permission_classes = [IsAdminUser]

    def post(self, request, albumId):
        try:
            # Lấy dữ liệu từ request
            title = request.data.get("title")
            description = request.data.get("description")
            singer = request.data.get("singer")
            thumbnail = request.FILES.get("thumbnail")
            audio = request.FILES.get("audio")
            
            # Kiểm tra album có tồn tại không
            album = get_object_or_404(Song, id=albumId)
            
            s3_service = AwsS3Service()
            thumbnailUrl = s3_service.save_file_to_s3(thumbnail)
            audioUrl = s3_service.save_file_to_s3(audio)

            # Tạo bài hát mới
            song = Song.objects.create(
                album=album,
                title=title,
                description=description,
                singer=singer,
                thumbnail_url=thumbnailUrl,
                audioUrl=audioUrl
            )

            # Trả về response
            serializer = SongSerializer(song)
            return Response({"message": "Song Added", "song": serializer.data}, status=status.HTTP_201_CREATED)
        except Exception as e:
            raise Exception(f"Unexpected error: {str(e)}")
        
class GetAllSongView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        songs = Song.objects.all()
        serializer = SongSerializer(songs, many=True)
       
        return Response(serializer.data)
    
class GetSongByIdView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, songId):
        song = get_object_or_404(Song, id=songId)
        serializer = SongSerializer(song)
       
        return Response(serializer.data) 

class DeleteSongByIdView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    
    def delete(self, request, songId):
        song = get_object_or_404(Song, id=songId)
        song.delete()
       
        return Response({"message": "Deleted successfully"}, status=status.HTTP_204_NO_CONTENT)