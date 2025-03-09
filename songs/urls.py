from django.urls import path
from .views import GetAllSongView, AddSongView, GetFeaturedView, GetMadeForYouView, GetTrendingView, GetSongView, DeleteSongView

urlpatterns = [
    path('', GetAllSongView.as_view(), name='get-all-song'),
    path('add-song/<uuid:userId>/<uuid:albumId>/', AddSongView.as_view(), name='add-song'),
    path('get-featured/', GetFeaturedView.as_view(), name='get-featured'),
    path('made-for-you/', GetMadeForYouView.as_view(), name='made-for-you'),
    path('trending/', GetTrendingView.as_view(), name='trending'),
    path('get-song/<uuid:songId>/', GetSongView.as_view(), name='get-song'),
    path('delete-song/<uuid:songId>/', DeleteSongView.as_view(), name='delete-song'),
]
