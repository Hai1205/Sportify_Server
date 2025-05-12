# Sportify Clone

## Overview

**Sportify** is a web-based music streaming application inspired by Spotify, offering a full range of features for music playback, song and album management, user interaction, and more.

- 🎵 **Music Playback**: Play, pause, skip to next or previous tracks with full control
- 🎧 **Now Playing View**: Display currently playing track with full song information
- 📚 **Browse Songs and Albums**: Explore a library of music content
- 🎤 **Song Detail Page**: View song lyrics and additional metadata
- 💿 **Album Detail Page**: See album tracklist and details
- 🔍 **Search**: Find songs, albums, and artists with ease
- ❤️ **Like**: Mark songs and albums as favorites
- 👤 **User & Artist Profiles**: View and manage personal or artist information
- 🔐 **Authentication System**: Secure sign-up and sign-in for users
- 💬 **Live Chat**: Send and receive messages between users in real time
- 📱 **Responsive Design**: Mobile-friendly interface that works on all screen sizes

## Technologies Used

boto3==1.37.5                      # AWS SDK for Python
botocore==1.37.5                   # Low-level core functionality of boto3
channels==4.2.0                    # Django support for WebSockets and real-time features
Django==5.1.6                      # Main web framework
djangorestframework_simplejwt==5.5.0  # JWT Authentication for DRF
mutagen==1.47.0                    # Audio metadata handling (e.g. MP3, FLAC tags)
PyMySQL==1.1.1                     # MySQL client library for Python
python-dotenv==1.1.0              # Load environment variables from .env files
requests==2.32.3                   # HTTP requests library

## Installation

### Prerequisites

- ✅ **Python 3.8 or higher** (Python **3.10+ is recommended** for best compatibility and performance)
- ✅ **pip** or **pipenv** for managing Python dependencies
- ✅ **MySQL 8.0 or higher** (MySQL **8.0+ is recommended** for full feature support)

### Steps

1. Clone the repository and navigate to the backend folder:

```bash
git clone https://github.com/Hai1205/Sportify_Server.git
cd Sportify_Server
```

2. Create and active virtual environment:

```bash 
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

3. Create and configure a `.env` file with the following variables:

```bash
SECRET_KEY=
CLIENT_PORT_3000=
AWS_S3_BUCKET_NAME=
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
```

4. Create database on MySQL:

```bash
CREATE DATABASE sportify CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

5. Running migrate and create admin account

```bash
python manage.py migrate
python manage.py createsuperuser
```

7. Running backend:

```bash
python manage.py runserver
```

8. Running WebSocket (ASGI):
open other terminal window to run venv and run the following command:


```bash
daphne -p 8001 Sportify_Server.asgi:application
```

## Team Members

| Student ID      | Full Name         | 
|-----------------|-------------------|
| 3122410095      | Nguyen Hoang Hai  |
| 3122410096      | Le Chi Hao        |
