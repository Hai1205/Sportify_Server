from rest_framework import serializers
from .models import Song

class SongSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    album = serializers.PrimaryKeyRelatedField(read_only=True)
    
    class Meta:
        model = Song
        fields = '__all__'