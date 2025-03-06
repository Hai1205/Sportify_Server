from django.urls import path
from .views import GetAllUserView, GetUserByIdView, UpdateUserByIdView, DeleteUserByIdView, GetSongByIdView

urlpatterns = [
    path('get-user-list/', GetAllUserView.as_view(), name='get-user-list'),
    path('get-user-by-id/<uuid:userId>/', GetUserByIdView.as_view(), name='get-user-by-id'),
    path('update-user-by-id/<uuid:userId>/', UpdateUserByIdView.as_view(), name='update-user-by-id'),
    path('delete-user-by-id/<uuid:userId>/', DeleteUserByIdView.as_view(), name='delete-user-by-id'),
    path('get-song-by-user-id/<uuid:userId>/', GetSongByIdView.as_view(), name='get-song-by-user-id'),
]
