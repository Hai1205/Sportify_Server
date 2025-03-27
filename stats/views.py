from rest_framework.permissions import IsAdminUser
from rest_framework.generics import GenericAPIView
from django.http import JsonResponse
from albums.models import Album
from songs.models import Song
from users.models import User
from users.serializers import FullInfoUserSerializer
from songs.serializers import FullInfoSongSerializer
from django.db.models import Count
from django.db.models import Q

class getGeneralStatView(GenericAPIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        try:
            totalSongs = Song.objects.count()
            totalAlbums = Album.objects.count()
            totalUsers = User.objects.count()
            totalArtists = User.objects.filter(role="artist").count()

            return JsonResponse({
                "status": 200,
                "message": "Get general statistics successfully",
                "generalStat": {
                    "totalAlbums": totalAlbums,
                    "totalSongs": totalSongs,
                    "totalUsers": totalUsers,
                    "totalArtists": totalArtists
                }
            }, safe=False, status=200)
        except Exception as e:
            return JsonResponse({
                "status": 500,
                "message": str(e)
            }, status=500)
            
class getPopularSongsStatView(GenericAPIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        try:
            userLimit = 5
            songs = Song.objects.annotate(view_count=Count('views')) \
                .order_by('-view_count')[:userLimit]

            serializer = FullInfoSongSerializer(songs, many=True)
            
            return JsonResponse({
                "status": 200,
                "message": "Get top song statistics successfully",
                "songs": serializer.data
            }, safe=False, status=200)

        except Exception as e:
            return JsonResponse({
                "status": 500,
                "message": str(e)
            }, status=500)
            
class getTopArtistsStatView(GenericAPIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        try:
            userLimit = 5
            users = User.objects.filter(role="artist") \
                .annotate(follower_count=Count('followers')) \
                .order_by('-follower_count')[:userLimit]

            serializer = FullInfoUserSerializer(users, many=True)
            
            return JsonResponse({
                "status": 200,
                "message": "Get top artist statistics successfully",
                "users": serializer.data
            }, safe=False, status=200)

        except Exception as e:
            return JsonResponse({
                "status": 500,
                "message": str(e)
            }, status=500)
