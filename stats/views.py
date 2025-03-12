from rest_framework.permissions import IsAdminUser
from rest_framework.generics import GenericAPIView
from django.http import JsonResponse
from albums.models import Album
from songs.models import Song
from users.models import User

class GetStatsView(GenericAPIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        try:
            totalSongs = Song.objects.count()
            totalAlbums = Album.objects.count()
            totalUsers = User.objects.count()

            # Lấy danh sách các artist duy nhất từ cả Song và Album
            uniqueArtists = (
                Song.objects.values_list("userId", flat=True).distinct()
            ).union(
                Album.objects.values_list("userId", flat=True).distinct()
            ).count()

            return JsonResponse({
                "status": 200,
                "message": "Get statistics successfully",
                "totalAlbums": totalAlbums,
                "totalSongs": totalSongs,
                "totalUsers": totalUsers,
                "totalArtists": uniqueArtists
            }, safe=False, status=200)
        except Exception as e:
            return JsonResponse({
                "status": 500,
                "message": str(e)
            }, status=500)
