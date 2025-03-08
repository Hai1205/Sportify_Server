from django.urls import path
from .views import RegisterView, RegisterAdminView, LoginView, LogoutView, TokenRefreshView, CheckAdmin

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('register-admin/', RegisterAdminView.as_view(), name='register-admin'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('refresh-token/', TokenRefreshView.as_view(), name='refresh'),
    path('check-admin/', CheckAdmin.as_view(), name='check-admin'),
]
