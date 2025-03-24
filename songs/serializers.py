from rest_framework import serializers
from .models import Song

class SongSerializer(serializers.ModelSerializer):
    class Meta:
        model = Song
        fields = '__all__'

class FullInfoSongSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    album = serializers.SerializerMethodField()
    
    class Meta:
        model = Song
        fields = ["id", "title", "genre", "releaseDate", "thumbnailUrl", "audioUrl", "videoUrl", "lyrics", "duration", "views", "created_at", "user", "album"]
    
    def get_user(self, obj):
        from users.serializers import UserSerializer
        from users.models import User
        
        user = User.objects.filter(songs=obj).first()
        
        return UserSerializer(user).data if user else None

    def get_album(self, obj):
        from albums.serializers import AlbumSerializer
        from albums.models import Album
        
        album = Album.objects.filter(songs=obj).first()
        
        return AlbumSerializer(album).data if album else None