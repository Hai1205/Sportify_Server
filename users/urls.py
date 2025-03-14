from django.urls import path
from .views import GetAllUserView, GetUserView, UpdateUserView, DeleteUserView, getAllUsersongView, FollowUserView, GetSuggestedUserView, RequireUpdateUserToArtistView, ResponseUpdateUserToArtistView

urlpatterns = [
    path('', GetAllUserView.as_view(), name='get-all-user'),
    path('get-user/<uuid:userId>/', GetUserView.as_view(), name='get-user'),
    path('update-user/<uuid:userId>/', UpdateUserView.as_view(), name='update-user'),
    path('delete-user/<uuid:userId>/', DeleteUserView.as_view(), name='delete-user'),
    path('follow-user/<uuid:currentUserId>/<uuid:opponentId>/', FollowUserView.as_view(), name='follow-user'),
    path('get-suggested-user/<uuid:userId>/', GetSuggestedUserView.as_view(), name='get-suggested-user'),
    path('get-user-songs/<uuid:userId>/', getAllUsersongView.as_view(), name='get-user-songs'),
    path('require-update-user-to-artist/<uuid:userId>/', RequireUpdateUserToArtistView.as_view(), name='require-update-user-to-artist'),
    path('response-update-user-to-artist/<uuid:userId>/', ResponseUpdateUserToArtistView.as_view(), name='response-update-user-to-artist'),
]
