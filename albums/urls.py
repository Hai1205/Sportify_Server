from django.urls import path
from .views import *

urlpatterns = [
    path('', GetAllAlbumView.as_view(), name='get-all-album'),
    path('upload-album/<uuid:userId>/', UploadAlbumView.as_view(), name='upload-album'),
    path('delete-album/<uuid:albumId>/', DeleteAlbumView.as_view(), name='delete-album'),
    path('get-album/<uuid:albumId>/', GetAlbumView.as_view(), name='get-album'),
    path('get-user-albums/<uuid:userId>/', GetUserAlbums.as_view(), name='get-user-albums'),
    path('get-user-liked-albums/<uuid:userId>/', GetUserLikedAlbumView.as_view(), name='get-user-liked-albums'),
    path('update-album/<uuid:albumId>/', updateAlbum.as_view(), name='update-album'),
    path('search-albums/', searchAlbums.as_view(), name='search-albums'),
    path('like-album/<uuid:userId>/<uuid:albumId>/', LikeSongView.as_view(), name='like-album'),
]
