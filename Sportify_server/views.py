from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

class HomeView(GenericAPIView):
    def get(self, request):
        return Response({"message": "Welcome to the API Home!"})