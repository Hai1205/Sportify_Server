from django.urls import path
from .views import *

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('login-with-google/', LoginWithGoogleView.as_view(), name='login-with-google'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('refresh-token/', TokenRefreshView.as_view(), name='refresh'),
    path('check-admin/', CheckAdmin.as_view(), name='check-admin'),
    path('check-artist/', CheckArtist.as_view(), name='check-artist'),
    path('change-password/<uuid:userId>/', ChangePasswordView.as_view(), name='change-password'),
    path('forgot-password/<uuid:userId>/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('reset-password/<uuid:userId>/', ResetPasswordView.as_view(), name='reset-password'),
    path('check-otp/<str:email>/', CheckOTPView.as_view(), name='check-otp'),
    path('send-otp/<str:email>/', SendOTPView.as_view(), name='send-otp'),
]
