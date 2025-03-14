from rest_framework import serializers
from .models import Song

class SongSerializer(serializers.ModelSerializer):
    class Meta:
        model = Song
        fields = '__all__'

class FullInfoAlbumSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    album = serializers.SerializerMethodField()
    
    class Meta:
        model = Song
        fields = '__all__'
    
    def get_user(self, obj):
        from users.serializers import UserSerializer  # Import tại đây để tránh vòng lặp
        return UserSerializer(obj.user).data

    def get_album(self, obj):
        from albums.serializers import AlbumSerializer  # Import tại đây để tránh vòng lặp
        return AlbumSerializer(obj.album).data