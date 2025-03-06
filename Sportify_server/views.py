from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
# from rest_framework.views import APIView
# from rest_framework.parsers import MultiPartParser
# from ..api.aws_s3_service import AwsS3Service
# from rest_framework.permissions import IsAuthenticated

class HomeView(GenericAPIView):
    def get(self, request):
        return Response({"message": "Welcome to the API Home!"})

# class UploadImageView(GenericAPIView):
#     permission_classes = [IsAuthenticated]
#     parser_classes = [MultiPartParser]

#     def post(self, request):
#         file = request.FILES.get("file")

#         if not file:
#             return Response({"error": "No file uploaded"}, status=400)

#         s3_service = AwsS3Service()
#         try:
#             file_url = s3_service.save_image_to_s3(file)
#             return Response({"url": file_url}, status=201)
#         except Exception as e:
#             return Response({"error": str(e)}, status=500)