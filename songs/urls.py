from django.urls import path
from .views import GetAllSongView, uploadSongView, GetFeaturedView, GetMadeForYouView, GetTrendingView, GetSongView, DeleteSongView

urlpatterns = [
    path('', GetAllSongView.as_view(), name='get-all-song'),
    path('upload-song/<uuid:userId>/<uuid:albumId>/', uploadSongView.as_view(), name='upload-song'),
    path('delete-song/<uuid:songId>/', DeleteSongView.as_view(), name='delete-song'),
    path('get-song/<uuid:songId>/', GetSongView.as_view(), name='get-song'),
    path('get-featured-songs/', GetFeaturedView.as_view(), name='get-featured-songs'),
    path('get-made-for-you-songs/', GetMadeForYouView.as_view(), name='get-made-for-you-songs'),
    path('get-trending-songs/', GetTrendingView.as_view(), name='get-trending-songs'),
]
