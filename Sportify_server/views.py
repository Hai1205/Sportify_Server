from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from django.http import HttpResponse
from rest_framework.permissions import AllowAny
from django.template.loader import render_to_string
from .services import AwsS3Service
import requests
from io import BytesIO
from django.core.mail import EmailMessage
from django.conf import settings

class HomeView(GenericAPIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        return Response({"message": "Welcome to the API Home!"})

class EmailView(GenericAPIView):
    permission_classes = [AllowAny]

    def post(self, request):
        send_from = settings.EMAIL_HOST_USER
        subject = 'Xác nhận đơn hàng'
        recipient_emails = ['hainguyenhoang1205@gmail.com', 'hainguyenhoang111@gmail.com']
        order_amount = '500,000 VND'
        order_code = 'DH123456'
        thumbnail = request.FILES.get("thumbnail")  # Ảnh upload từ form
        
        s3_service = AwsS3Service()
        thumbnailUrl = s3_service.save_file_to_s3(thumbnail)  # Lưu ảnh lên S3 và lấy URL

        # Render template HTML
        html_content = render_to_string('mail_template.html', {
            'order_code': order_code,
            'order_amount': order_amount,
            'thumbnailUrl': thumbnailUrl  # Hiển thị ảnh trong email
        })

        # Tạo email
        email_message = EmailMessage(
            subject,
            html_content,
            send_from,
            recipient_emails
        )
        email_message.content_subtype = "html"  # Email ở dạng HTML

        # Tải file từ S3 và đính kèm vào email
        response = requests.get(thumbnailUrl)
        if response.status_code == 200:
            file_data = BytesIO(response.content)
            email_message.attach("thumbnail.png", file_data.getvalue(), "image/png")  # Đính kèm file
        
        email_message.send()
        return HttpResponse('Email sent successfully!')