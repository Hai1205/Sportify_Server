from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from django.http import HttpResponse
from rest_framework.permissions import AllowAny
from .services import mailService
from .services import AwsS3Service

class HomeView(GenericAPIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        return Response({"message": "Welcome to the API Home!"})

class EmailView(GenericAPIView):
    permission_classes = [AllowAny]

    def post(self, request):
        recipient_emails = ['hainguyenhoang1205@gmail.com', 'hainguyenhoang111@gmail.com']
        order_amount = '500,000 VND'
        order_code = 'DH123456'
        thumbnail = request.FILES.get("thumbnail")  # Ảnh upload từ form
        
        s3_service = AwsS3Service()
        thumbnailUrl = s3_service.save_file_to_s3(thumbnail) 
        mailService.test(order_code, order_amount, thumbnailUrl, recipient_emails)
        
        return HttpResponse('Email sent successfully!')
    
class MailActive(GenericAPIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        OTP=123456
        recipient="hainguyenhoang1205@gmail.com"
        mailService.mailActiveAccount(OTP, recipient)
        return HttpResponse('Email sent successfully!')
