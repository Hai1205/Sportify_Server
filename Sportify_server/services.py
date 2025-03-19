import boto3
import uuid
import os
from django.conf import settings
from botocore.exceptions import BotoCoreError, NoCredentialsError
import requests
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
import requests
from io import BytesIO
from django.core.mail import EmailMessage
from django.conf import settings
import random
import string

class ultils:
    @staticmethod
    def generate_password(length=10):
        characters = string.ascii_letters + string.digits  # Chứa cả chữ hoa, chữ thường và số
        password = ''.join(random.choices(characters, k=length))
        return password
    
    @staticmethod
    def generate_OTP(length=6):
        characters = string.digits
        password = ''.join(random.choices(characters, k=length))
        return password

class AwsS3Service:
    def __init__(self):
        self.bucket_name = settings.AWS_S3_BUCKET_NAME
        self.aws_access_key = settings.AWS_ACCESS_KEY_ID
        self.aws_secret_key = settings.AWS_SECRET_ACCESS_KEY
        self.region_name = "ap-southeast-1"
        self.bucket_url = f"https://{self.bucket_name}.s3.amazonaws.com/"

        # Khởi tạo client S3
        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id=self.aws_access_key,
            aws_secret_access_key=self.aws_secret_key,
            region_name=self.region_name,
        )

    def save_file_to_s3(self, file):
        try:
            file_extension = os.path.splitext(file.name)[1].lower()
            allowed_extensions = [".jpg", ".jpeg", ".png", ".mp3"]
            
            if file_extension not in allowed_extensions:
                raise ValueError("Only accept files with format JPG, JPEG, PNG, or MP3")

            # Tạo tên file duy nhất
            s3_file_name = f"{uuid.uuid4()}{file_extension}"

            # Xác định ContentType
            content_type = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".mp3": "audio/mpeg"
            }.get(file_extension, "binary/octet-stream")

            # Upload file
            self.s3_client.upload_fileobj(
                file,
                self.bucket_name,
                s3_file_name,
                # ExtraArgs={"ContentType": content_type, "ACL": "public-read"},
                ExtraArgs={"ContentType": content_type},
            )

            return f"{self.bucket_url}{s3_file_name}"

        except NoCredentialsError:
            raise Exception("AWS credentials not found. Please check your settings.")
        except BotoCoreError as e:
            raise Exception(f"Error uploading file to S3: {str(e)}")
        except Exception as e:
            raise Exception(f"Unexpected error: {str(e)}")

    def delete_file_from_s3(self, file_url):
        try:
            file_name = file_url.replace(self.bucket_url, "")

            self.s3_client.delete_object(Bucket=self.bucket_name, Key=file_name)

        except NoCredentialsError:
            raise Exception("AWS credentials not found. Please check your settings.")
        except BotoCoreError as e:
            raise Exception(f"Error deleting file from S3: {str(e)}")
        except Exception as e:
            raise Exception(f"Unexpected error: {str(e)}")

    def download_file_from_s3(self, file_url, local_filename):
        from pathlib import Path
        # Lấy thư mục Downloads của người dùng
        downloads_folder = str(Path.home() / "Downloads")
        
        # Tạo đường dẫn đầy đủ cho file tải về
        file_path = os.path.join(downloads_folder, local_filename)
        
        # Gửi request tải file
        response = requests.get(file_url, stream=True)
        if response.status_code == 200:
            with open(file_path, "wb") as file:
                for chunk in response.iter_content(1024):
                    file.write(chunk)
            print(f"File downloaded: {file_path}")  # In ra đường dẫn file đã lưu
        else:
            print("Download failed")
            
class mailService:
    @staticmethod
    def test(order_code, order_amount, thumbnailUrl, recipient_emails):
        send_from = settings.EMAIL_HOST_USER
        subject = 'Order Details'

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
        
    @staticmethod
    def mailActiveAccount(OTP, recipient):
        send_from = settings.EMAIL_HOST_USER
        subject = 'Active Account'
        recipient_emails = [recipient,]

        html_content = render_to_string('mail_active_account.html', {
            'OTP': OTP,
        })

        # Tạo email
        email_message = EmailMessage(
            subject,
            html_content,
            send_from,
            recipient_emails
        )
        email_message.content_subtype = "html"  # Email ở dạng HTML
        
        email_message.send()
        
    @staticmethod
    def mailResetPassword(password, recipient):
        send_from = settings.EMAIL_HOST_USER
        subject = 'Active Account'
        recipient_emails = [recipient,]

        html_content = render_to_string('mail_password.html', {
            'password': password,
        })

        # Tạo email
        email_message = EmailMessage(
            subject,
            html_content,
            send_from,
            recipient_emails
        )
        email_message.content_subtype = "html"  # Email ở dạng HTML
        
        email_message.send()
    