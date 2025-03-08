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
            total_songs = Song.objects.count()
            total_albums = Album.objects.count()
            total_users = User.objects.count()

            # Lấy danh sách các artist duy nhất từ cả Song và Album
            unique_artists = (
                Song.objects.values_list("artist", flat=True).distinct()
            ).union(
                Album.objects.values_list("artist", flat=True).distinct()
            ).count()

            return JsonResponse({
                "totalAlbums": total_albums,
                "totalSongs": total_songs,
                "totalUsers": total_users,
                "totalArtists": unique_artists
            })
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
