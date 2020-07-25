"""
WSGI config for book project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

import birdseye.server
from werkzeug.middleware.dispatcher import DispatcherMiddleware

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'book.settings')

application = DispatcherMiddleware(get_wsgi_application(), {
    '/birdseye': birdseye.server.app
})
