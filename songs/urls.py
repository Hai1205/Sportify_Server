from django.urls import path
from .views import GetAllSongView, AddSongView, GetSongByIdView, DeleteSongByIdView

urlpatterns = [
    path('get-all-song/', GetAllSongView.as_view(), name='get-all-song'),
    path('add-song/<uuid:albumId>/', AddSongView.as_view(), name='add-song'),
    path('get-song-by-id/<uuid:songId>/', GetSongByIdView.as_view(), name='get-song-by-id'),
    path('delete-song-by-id/<uuid:songId>/', DeleteSongByIdView.as_view(), name='delete-song-by-id'),
]
