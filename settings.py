from pathlib import Path

# Base dir (settings.py is next to manage.py)
BASE_DIR = Path(__file__).resolve().parent

# Minimal required settings
SECRET_KEY = 'django-insecure-replace-me'
DEBUG = True

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'bootstrap5',
    'appointments',
    'multiselectfield',
]

# Allow hosts for local network development. Replace or restrict in production.
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']

# Middleware required by admin/auth
MIDDLEWARE = [
    'appointments.middleware.DatabaseAvailabilityMiddleware',  # catch DB errors and show friendly page
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',            # must come before AuthenticationMiddleware
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',         # required for admin/auth
    'django.contrib.messages.middleware.MessageMiddleware',            # required for admin/messages
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'urls'  # urls.py sits next to manage.py/settings.py

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',   # required by admin
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_USER_MODEL = 'appointments.User'

# Static (basic)
STATIC_URL = '/static/'