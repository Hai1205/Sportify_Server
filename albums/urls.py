from django.urls import path
from .views import CreateAlbumView, GetAllAlbumView, GetAlbumView, DeleteAlbumView

urlpatterns = [
    path('', GetAllAlbumView.as_view(), name='get-all-album'),
    path('create-album/<uuid:userId>/', CreateAlbumView.as_view(), name='create-album'),
    path('get-album/<uuid:albumId>/', GetAlbumView.as_view(), name='get-album'),
    path('delete-album/<uuid:albumId>/', DeleteAlbumView.as_view(), name='delete-album'),
]
