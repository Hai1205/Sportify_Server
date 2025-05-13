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
from datetime import datetime

class utils:
    @staticmethod
    def generate_password(length=10):
        characters = string.ascii_letters + string.digits
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

        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id=self.aws_access_key,
            aws_secret_access_key=self.aws_secret_key,
            region_name=self.region_name,
        )

    def save_file_to_s3(self, file):
        try:
            file_extension = os.path.splitext(file.name)[1].lower()
            
            allowed_extensions = [".jpg", ".jpeg", ".png", ".mp3", ".mp4", ".avi", ".mov"]

            if file_extension not in allowed_extensions:
                raise ValueError("Only accept files with format JPG, JPEG, PNG, MP3, MP4, AVI, or MOV")

            s3_file_name = f"{uuid.uuid4()}{file_extension}"

            content_type = {
                ".jpg": "image/jpeg",
                ".jpeg": "image/jpeg",
                ".png": "image/png",
                ".mp3": "audio/mpeg",
                ".mp4": "video/mp4",
                ".avi": "video/x-msvideo",
                ".mov": "video/quicktime",
            }.get(file_extension, "binary/octet-stream")

            self.s3_client.upload_fileobj(
                file,
                self.bucket_name,
                s3_file_name,
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

    def download_file_from_s3(self, file_url):
        try:
            response = requests.get(file_url, stream=True)
            if response.status_code == 200:
                return response.content
            else:
                raise Exception("Download failed, status code: " + str(response.status_code))
        except Exception as e:
            raise Exception(f"Error downloading file from S3: {str(e)}")

class mailService:
    @staticmethod
    def test(order_code, order_amount, thumbnailUrl, recipient_emails):
        send_from = settings.EMAIL_HOST_USER
        subject = 'Order Details'

        html_content = render_to_string('mail_template.html', {
            'order_code': order_code,
            'order_amount': order_amount,
            'thumbnailUrl': thumbnailUrl 
        })

        email_message = EmailMessage(
            subject,
            html_content,
            send_from,
            recipient_emails
        )
        email_message.content_subtype = "html" 

        response = requests.get(thumbnailUrl)
        if response.status_code == 200:
            file_data = BytesIO(response.content)
            email_message.attach("thumbnail.png", file_data.getvalue(), "image/png")  
        
        email_message.send()
        
    @staticmethod
    def mailActiveAccount(OTP, recipient_name, sender_name, recipient_email):
        send_from = settings.EMAIL_HOST_USER
        subject = 'Active Account'
        recipient_emails = [recipient_email,]

        html_content = render_to_string('mail_active_account.html', {
            'OTP': OTP,
            'recipient_name': recipient_name,
            'year': datetime.now().year,
            'organization': "Sportify",
            'sender_name': sender_name,
        })

        email_message = EmailMessage(
            subject,
            html_content,
            send_from,
            recipient_emails
        )
        email_message.content_subtype = "html" 
        
        email_message.send()
        
    @staticmethod
    def mailResetPassword(recipient_email, password, recipient_name, sender_name):
        send_from = settings.EMAIL_HOST_USER
        subject = 'Reset Password'
        recipient_emails = [recipient_email,]

        html_content = render_to_string('mail_reset_password.html', {
            'recipient_email': recipient_email,
            'password': password,
            'recipient_name': recipient_name,
            'year': datetime.now().year,
            'organization': "Sportify",
            'sender_name': sender_name,
        })

        email_message = EmailMessage(
            subject,
            html_content,
            send_from,
            recipient_emails
        )
        email_message.content_subtype = "html" 
        
        email_message.send()
        
    @staticmethod
    def mailApproveArtist(recipient_name, sender_name, recipient_email, details):
        send_from = settings.EMAIL_HOST_USER
        subject = 'Approve Artist'
        recipient_emails = [recipient_email,]

        html_content = render_to_string('mail_approve_artist.html', {
            'recipient_name': recipient_name,
            'sender_name': sender_name,
            'organization': "Sportify",
            'year': datetime.now().year,
            'recipient_email': recipient_email,
            'details': details,
        })

        email_message = EmailMessage(
            subject,
            html_content,
            send_from,
            recipient_emails
        )
        email_message.content_subtype = "html" 
        
        email_message.send()
        
    @staticmethod
    def mailRejectArtist(recipient_name, sender_name, recipient_email, details, reason_reject):
        send_from = settings.EMAIL_HOST_USER
        subject = 'Reject Artist'
        recipient_emails = [recipient_email,]

        html_content = render_to_string('mail_reject_artist.html', {
            'recipient_name': recipient_name,
            'sender_name': sender_name,
            'organization': "Sportify",
            'year': datetime.now().year,
            'recipient_email': recipient_email,
            'details': details,
            'reason_reject': reason_reject,
        })

        email_message = EmailMessage(
            subject,
            html_content,
            send_from,
            recipient_emails
        )
        email_message.content_subtype = "html" 
        
        email_message.send()
    