from rest_framework import serializers
from songs.serializers import SongSerializer
from .models import Album

class FullInfoAlbumSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    songs = SongSerializer(many=True, read_only=True)

    class Meta:
        model = Album
        fields = ["id", "title", "releaseDate", "thumbnailUrl", "created_at", "user", "songs"]

    def get_user(self, obj):
        from users.serializers import UserSerializer
        from users.models import User
        
        user = User.objects.filter(albums=obj).first()
        
        return UserSerializer(user).data if user else None
    
class AlbumSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Album
        fields = '__all__'