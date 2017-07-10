import django, sys, os
from django.conf import settings

BASE_DIR = os.path.dirname(__file__)
SECRET_KEY = '--'

DEBUG=True
DATABASES={
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
    }
}
ROOT_URLCONF='tests.urls'
INSTALLED_APPS=[
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'drf_ng_generator',
    'rest_framework_swagger',
    'tests'
]
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(os.path.dirname(__file__), 'drf_ng_generator')
        ],
        'APP_DIRS': True
    },
]
