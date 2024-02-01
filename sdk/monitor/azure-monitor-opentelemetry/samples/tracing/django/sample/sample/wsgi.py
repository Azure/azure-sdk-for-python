# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""
WSGI config for sample project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/wsgi/
"""

import os

from azure.monitor.opentelemetry import configure_azure_monitor
from django.core.wsgi import get_wsgi_application


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sample.settings")

# Configure Azure monitor collection telemetry pipeline
# configure_azure_monitor should only be called once in either asgi.py, wsgi.py, or manage.py, depending on startup method.
# If using wsgi, please remove configure_azure_monitor from asgi.py and manage.py
configure_azure_monitor()

application = get_wsgi_application()
