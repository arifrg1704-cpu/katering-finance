import os
from .settings import BASE_DIR

DEBUG = False

# Tambahkan domain pythonanywhere Anda di sini
ALLOWED_HOSTS = ['argx2works.pythonanywhere.com', 'localhost', '127.0.0.1']

# Agar Static Files terbaca di PythonAnywhere, kita set STATIC_ROOT
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
