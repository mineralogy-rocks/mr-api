from .base import *
import os

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration


sentry_sdk.init(
    dsn=os.environ.get('DJANGO_SENTRY_DSN', default=None),
    environment=os.environ.get('DJANGO_SENTRY_ENV', default=''),
    integrations=[DjangoIntegration()]
)


AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')

AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
AWS_S3_ENDPOINT_URL = os.environ.get('AWS_S3_ENDPOINT_URL')
AWS_S3_OBJECT_PARAMETERS = {'CacheControl': 'max-age=86400', }

AWS_LOCATION = 'static'
AWS_DEFAULT_ACL = 'public-read'
AWS_QUERYSTRING_AUTH = False

STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

STATIC_URL = '{}/{}/'.format(AWS_S3_ENDPOINT_URL, AWS_LOCATION)
STATIC_ROOT = ''
