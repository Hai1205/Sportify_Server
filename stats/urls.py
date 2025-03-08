from django.urls import path
from .views import GetStatsView

urlpatterns = [
    path('', GetStatsView.as_view(), name='get-stats'),
]