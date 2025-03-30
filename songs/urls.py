from django.urls import path
from .views import *

urlpatterns = [
    path('', GetAllSongView.as_view(), name='get-all-song'),
    path('upload-song/<uuid:userId>/', uploadSongView.as_view(), name='upload-song'),
    path('delete-song/<uuid:songId>/', DeleteSongView.as_view(), name='delete-song'),
    path('get-song/<uuid:songId>/', GetSongView.as_view(), name='get-song'),
    path('get-featured-songs/', GetFeaturedView.as_view(), name='get-featured-songs'),
    path('get-made-for-you-songs/', GetMadeForYouView.as_view(), name='get-made-for-you-songs'),
    path('get-trending-songs/', GetTrendingView.as_view(), name='get-trending-songs'),
    path('update-song/<uuid:songId>/', UpdateSongView.as_view(), name='update-song'),
    path('add-song-to-album/<uuid:songId>/<uuid:albumId>/', AddSongToAlbumView.as_view(), name='add-song-to-album'),
    path('like-song/<uuid:userId>/<uuid:songId>/', LikeSongView.as_view(), name='like-song'),
    path('download-song/<uuid:songId>/', DownloadSongView.as_view(), name='download-song'),
    path('search-songs/', SearchSongsView.as_view(), name='search-songs'),
    path('increase-song-view/<uuid:songId>/', IncreaseSongViewView.as_view(), name='increase-song-view'),
]
