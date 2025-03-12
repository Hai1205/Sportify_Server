from rest_framework import serializers
from songs.serializers import SongSerializer
from .models import Album
class AlbumSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    songs = SongSerializer(many=True, read_only=True)
    
    class Meta:
        model = Album
        fields = '__all__'
        
class GetAllSongByAlbumIdSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    songs = SongSerializer(many=True, read_only=True)

    class Meta:
        model = Album
        fields = '__all__'