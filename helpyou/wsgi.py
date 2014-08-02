"""
WSGI config for helpyou project.

This module contains the WSGI application used by Django's development server
and any production WSGI deployments. It should expose a module-level variable
named ``application``. Django's ``runserver`` and ``runfcgi`` commands discover
this application via the ``WSGI_APPLICATION`` setting.

Usually you will have the standard Django WSGI application here, but it also
might make sense to replace the whole Django WSGI application with a custom one
that later delegates to the Django one. For example, you could introduce WSGI
middleware here, or combine a Django application with an application of another
framework.

"""
import os

# Add the site-packages of the chosen virtualenv to work with
import site
import sys

# site.addsitedir('/home/mehelp5/dVLU4yf1mr47FdacwqjQYw/help_env/lib/python2.6/site-packages')
#
# # Add the app's directory to the PYTHONPATH
sys.path.append('/root/mehelpyou/')
#
# # Activate your virtual env
# activate_env=os.path.expanduser("/home/mehelp5/dVLU4yf1mr47FdacwqjQYw/help_env/bin/activate_this.py")
# execfile(activate_env, dict(__file__=activate_env))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "helpyou.settings")

# This application object is used by any WSGI server configured to use this
# file. This includes Django's development server, if the WSGI_APPLICATION
# setting points here.
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

# Apply WSGI middleware here.
# from helloworld.wsgi import HelloWorldApplication
# application = HelloWorldApplication(application)
