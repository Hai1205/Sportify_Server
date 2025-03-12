from django.urls import path
from .views import UploadAlbumView, GetAllAlbumView, GetAlbumView, DeleteAlbumView

urlpatterns = [
    path('', GetAllAlbumView.as_view(), name='get-all-album'),
    path('upload-album/<uuid:userId>/', UploadAlbumView.as_view(), name='upload-album'),
    path('delete-album/<uuid:albumId>/', DeleteAlbumView.as_view(), name='delete-album'),
    path('get-album/<uuid:albumId>/', GetAlbumView.as_view(), name='get-album'),
]
