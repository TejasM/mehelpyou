# Django settings for helpyou project.
import os
import django
import sys

DJANGO_ROOT = os.path.dirname(os.path.realpath(django.__file__))
SITE_ROOT = os.path.dirname(os.path.realpath(__file__))

import djcelery

djcelery.setup_loader()

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
# ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'
        'NAME': 'mehelp5_help', # Or path to database file if using sqlite3.
        # The following settings are not used with sqlite3:
        'USER': 'mehelp5_tejas',
        'PASSWORD': 'tejas',
        'HOST': '', # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        'PORT': '', # Set to empty string for default.
    }
}

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
#         'NAME': os.path.join(SITE_ROOT, 'database'), # Or path to database file if using sqlite3.
#     }
# }

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = ['www.mehelpyou.com', 'mehelpyou.com']

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'America/New_York'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
MEDIA_ROOT = os.path.join(SITE_ROOT, '../avatars/')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://example.com/media/", "http://media.example.com/"
MEDIA_URL = 'avatars/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/var/www/example.com/static/"
STATIC_ROOT = ''

# URL prefix for static files.
# Example: "http://example.com/static/", "http://static.example.com/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    os.path.join(SITE_ROOT, '../static/'),
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    #    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'xiq*##5ldj(a92-$7+xuid3dm-4^w&hu_&p(#4h1a!0ti^aqr5'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    #     'django.template.loaders.eggs.Loader',
)

RATE = 1

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'helpyou.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'helpyou.wsgi.application'

TEMPLATE_DIRS = (
    os.path.join(SITE_ROOT, '../templates'),
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.request',
    'django.contrib.messages.context_processors.messages',
    'helpyou.mehelpyou.context_processors.feature_context_processor'
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    'helpyou.mehelpyou',
    'helpyou.request',
    'helpyou.response',
    'helpyou.userprofile',
    'helpyou.index',
    'south',
    'social_auth',
    'django.contrib.staticfiles',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
    "django_forms_bootstrap",
    "payments",
    "mathfilters",
    "helpyou.notifications",
    'django_filters',
    'mailer',
    'djcelery',
    'helpyou.group',
    'pytz'
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

LOGIN_URL = '/users/login'
LOGIN_REDIRECT_URL = '/users/login'
LOGIN_ERROR_URL = '/'

AUTHENTICATION_BACKENDS = (
    'social_auth.backends.twitter.TwitterBackend',
    'social_auth.backends.facebook.FacebookBackend',
    'social_auth.backends.contrib.linkedin.LinkedinBackend',
    'django.contrib.auth.backends.ModelBackend',
)

TWITTER_CONSUMER_KEY = 'phYQOWa0275clxNNPRz0rw'
TWITTER_CONSUMER_SECRET = '0vvkv6vGm2G9o1tLMtyn7KzObcmKEaMmK2MeAz3DdSw'
FACEBOOK_APP_ID = '156278484571544'
FACEBOOK_API_SECRET = '48bf190098d0f48cfdc044613fe2c7c9'
FACEBOOK_EXTENDED_PERMISSIONS = ['email', ]

LINKEDIN_CONSUMER_KEY = '03ms6ze0xcna'
LINKEDIN_CONSUMER_SECRET = 'I7izwd2Pqkjp3Au1'

LINKEDIN_SCOPE = ['r_fullprofile', 'r_emailaddress', 'rw_groups', 'r_network', 'w_messages', 'r_basicprofile']
# Add the fields so they will be requested from linkedin.
LINKEDIN_EXTRA_FIELD_SELECTORS = ['email-address', 'headline', 'industry', 'interests',
                                  'skills', 'educations', 'num-recommenders', 'recommendations-received',
                                  'num-connections', 'connections', 'picture-url']
# Arrange to add the fields to UserSocialAuth.extra_data
LINKEDIN_EXTRA_DATA = [('id', 'id'),
                       ('first-name', 'first_name'),
                       ('last-name', 'last_name'),
                       ('email-address', 'email_address'),
                       ('headline', 'headline'),
                       ('industry', 'industry'),
                       ('interests', 'interests'),
                       ('skills', 'skills'),
                       ('educations', 'educations'),
                       ('num-recommenders', 'num_recommenders'),
                       ('recommendations-received', 'recommendations_received'),
                       ('num-connections', 'num_connections'),
                       ('connections', 'connections'),
                       ('profile-picture', 'profile_picture')]

TWITTER_EXTRA_DATA = [('profile_image_url', 'profile_picture')]

SOCIAL_AUTH_PIPELINE = (
    'social_auth.backends.pipeline.social.social_auth_user',
    'social_auth.backends.pipeline.user.get_username',
    'social_auth.backends.pipeline.associate.associate_by_email',
    'social_auth.backends.pipeline.user.create_user',
    'social_auth.backends.pipeline.social.associate_user',
    'social_auth.backends.pipeline.social.load_extra_data',
    'social_auth.backends.pipeline.user.update_user_details'
)

STRIPE_PUBLIC_KEY = "pk_test_HlXsmOAZkKNhrPmUQ7w8Iumi"
STRIPE_SECRET_KEY = "sk_test_wQyxu2ZMVuK9ynbiFQTc2FOz"

SOUTH_DATABASE_ADAPTERS = {'default': 'south.db.postgresql_psycopg2'}

BROKER_HOST = "localhost"
BROKER_PORT = 5672
BROKER_PASSWORD = "guest"
BROKER_USER = "guest"
BROKER_VHOST = "vhost"
BROKER_URL = "amqp://guest:guest@localhost:5672//"

CELERY_RESULT_BACKEND = "amqp"
CELERY_IMPORTS = ("tasks", )
CELERY_ALWAYS_EAGER = True
# smtp settings for email
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'mail.mehelpyou.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'info@mehelpyou.com'
EMAIL_HOST_PASSWORD = 'tejas'
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = 'info@mehelpyou.com'

sys.path.append(os.path.dirname(__file__))

# ########## END TOOLBAR CONFIGURATION
# import dj_database_url
# #
# #
# DATABASES['default'] = dj_database_url.config()
# # # # Honor the 'X-Forwarded-Proto' header for request.is_secure()
# SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
#
# SOCIAL_AUTH_REDIRECT_IS_HTTPS = True
NOTE = "\n\nWe value your input and patronage. Please feel free to provide us feedback through our website or to email us at info@MeHelpYou.com." + "\n\nYours Sincerely,\nThe MeHelpYou Team\n\n'We are here to help you'"


def ForgotEmail(username, link):
    return "Dear " + username + ": \n\nThank-you for requesting to reset your password. To complete the process, please " \
                                "click on the following link, which will enable you to enter a new password: " + link + NOTE


def ResponseToRequest(username, title, link):
    return "Dear " + username + ": \n\nCongratulations! There is a response to your Request for " + title + " at www.MeHelpYou.com.\n\nPlease visit the following link to view the response: " + link + NOTE


def ResponseBought(username, buyer, title, link, price):
    return "Dear " + username + ": \n\nCongratulations! Your response to " + buyer + "'s Request for " + title + " has been bought and you have received " + price + "points at www.MeHelpYou.com.\n\n" + \
           "Please visit the following link to view the response: " + link + NOTE


def ResponseNegotiate(username, title, link, price):
    return "Dear " + username + ",\n\nCongratulations! A reward negotiation has started for your response to Request " + title + " at " + price + "points at www.MeHelpYou.com. \n\nPlease visit the following link to view the negotiation and determine if you would like to agree, disagree, or further negotiate: " + link + NOTE


def ResponseCounterNegotiate(username, title, link, price):
    return "Dear " + username + ",\n\nCongratulations! A counter-offer to a negotiation has been made on response to your Request for " + title + "points at www.MeHelpYou.com.\n\nPlease visit the following link to view the negotiation and determine if you would like to agree, disagree, or further negotiate: " + link + NOTE