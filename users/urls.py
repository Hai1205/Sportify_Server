from django.urls import path
from .views import GetAllUserView, GetUserView, UpdateUserView, DeleteUserView, GetUserSongView, UpdateUserToArtistView

urlpatterns = [
    path('', GetAllUserView.as_view(), name='get-all-user'),
    path('get-user/<uuid:userId>/', GetUserView.as_view(), name='get-user'),
    path('update-user/<uuid:userId>/', UpdateUserView.as_view(), name='update-user'),
    path('delete-user/<uuid:userId>/', DeleteUserView.as_view(), name='delete-user'),
    path('get-user-song/<uuid:userId>/', GetUserSongView.as_view(), name='get-user-song'),
    path('update-to-artist/<uuid:userId>/', UpdateUserToArtistView.as_view(), name='update-to-artist'),
]
