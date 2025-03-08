from rest_framework import serializers
from songs.serializers import SongSerializer
from .models import Album

class AlbumSerializer(serializers.ModelSerializer):
    class Meta:
        model = Album
        fields = '__all__'
        
class GetAllSongByAlbumIdSerializer(serializers.ModelSerializer):
    songs = SongSerializer(many=True, read_only=True)  # Lấy danh sách bài hát của album

    class Meta:
        model = Album
        fields = '__all__'