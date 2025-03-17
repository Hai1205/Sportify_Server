from django.urls import path
from .views import UploadAlbumView, \
                    GetAllAlbumView, \
                    GetAlbumView, \
                    GetUserAlbums, \
                    DeleteAlbumView, \
                    updateAlbum, \
                    searchAlbums

urlpatterns = [
    path('', GetAllAlbumView.as_view(), name='get-all-album'),
    path('upload-album/<uuid:userId>/', UploadAlbumView.as_view(), name='upload-album'),
    path('delete-album/<uuid:albumId>/', DeleteAlbumView.as_view(), name='delete-album'),
    path('get-album/<uuid:albumId>/', GetAlbumView.as_view(), name='get-album'),
    path('get-user-albums/<uuid:userId>/', GetUserAlbums.as_view(), name='get-user-albums'),
    path('update-album/<uuid:albumId>/', updateAlbum.as_view(), name='update-album'),
    path('search-albums/', searchAlbums.as_view(), name='search-albums'),
]
