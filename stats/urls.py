from django.urls import path
from .views import *

urlpatterns = [
    path('', getGeneralStatView.as_view(), name='get-general-stat'),
    path('get-popular-songs-stat/', getPopularSongsStatView.as_view(), name='get-popular-songs-stat'),
    path('get-top-artists-stat/', getTopArtistsStatView.as_view(), name='get-top-artists-stat'),
]