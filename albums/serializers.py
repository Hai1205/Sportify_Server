from rest_framework import serializers
from songs.serializers import SongSerializer
from .models import Album

class FullInfoAlbumSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    songs = SongSerializer(many=True, read_only=True)
    
    class Meta:
        model = Album
        fields = '__all__'
    
    def get_user(self, obj):
        from users.serializers import UserSerializer  # Import tại đây để tránh vòng lặp
        return UserSerializer(obj.user).data
    
class AlbumSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Album
        fields = '__all__'