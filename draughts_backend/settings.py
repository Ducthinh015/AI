import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'your-secret-key'
DEBUG = True
ALLOWED_HOSTS = ['*']  # Có thể giới hạn sau khi deploy

# Ứng dụng cài đặt
 INSTALLED_APPS = [
-    'corsheaders',  # CORS nên nằm trên cùng
+    'corsheaders',        # CORS nên nằm đầu
     'django.contrib.auth',
     'django.contrib.contenttypes',
     'django.contrib.sessions',
     'django.contrib.messages',
     'django.contrib.staticfiles',
     'rest_framework',
     'game',
 ]

 MIDDLEWARE = [
     'corsheaders.middleware.CorsMiddleware',  # Nên nằm đầu
     'django.middleware.common.CommonMiddleware',
     'django.contrib.sessions.middleware.SessionMiddleware',
     'django.middleware.csrf.CsrfViewMiddleware',
     'django.contrib.auth.middleware.AuthenticationMiddleware',
     'django.contrib.messages.middleware.MessageMiddleware',
 ]

 # Cho phép tất cả origin gọi API (chỉ dev)
 CORS_ALLOW_ALL_ORIGINS = True
+CORS_ALLOW_CREDENTIALS = True
 CORS_ALLOW_HEADERS = list(default_headers) + [
     # nếu cần thêm header
 ]

 REST_FRAMEWORK = {
     'DEFAULT_RENDERER_CLASSES': (
         'rest_framework.renderers.JSONRenderer',
         'rest_framework.renderers.BrowsableAPIRenderer',
     ),
+    # Tắt authentication/permission mặc định để frontend gọi dễ
+    'DEFAULT_AUTHENTICATION_CLASSES': [],
+    'DEFAULT_PERMISSION_CLASSES': [],
 }

