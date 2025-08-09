import os
from decouple import config

# Database configuration for Docker environment
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': config('MYSQL_DB', default='messaging_app_db'),
        'USER': config('MYSQL_USER', default='messaging_user'),
        'PASSWORD': config('MYSQL_PASSWORD', default='password'),
        'HOST': config('MYSQL_HOST', default='localhost'),
        'PORT': config('MYSQL_PORT', default='3306'),
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

# Alternative configuration using environment variables directly
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': os.environ.get('MYSQL_DB', 'messaging_app_db'),
#         'USER': os.environ.get('MYSQL_USER', 'messaging_user'),
#         'PASSWORD': os.environ.get('MYSQL_PASSWORD', 'password'),
#         'HOST': os.environ.get('MYSQL_HOST', 'localhost'),
#         'PORT': os.environ.get('MYSQL_PORT', '3306'),
#         'OPTIONS': {
#             'charset': 'utf8mb4',
#             'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
#         },
#     }
# }
