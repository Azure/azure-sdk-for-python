# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License in the project root for
# license information.
# --------------------------------------------------------------------------

"""Simple Django app demonstrating Browser SDK loader integration.

Set APPLICATIONINSIGHTS_CONNECTION_STRING before running this sample.
Then run:
    python http_django_browser_sdk_loader.py

Open http://127.0.0.1:8000/ and inspect page source to verify the
Application Insights browser snippet was injected before </head>.
"""

from django.conf import settings  # pylint: disable=import-error
from django.core.management import execute_from_command_line  # pylint: disable=import-error
from django.http import HttpResponse  # pylint: disable=import-error
from django.urls import path  # pylint: disable=import-error

from azure.monitor.opentelemetry import configure_azure_monitor


def index(_request):
    return HttpResponse(
        """<!DOCTYPE html>
<html>
<head>
    <meta charset=\"utf-8\" />
    <title>Azure Monitor Browser SDK Loader Sample</title>
</head>
<body>
    <h1>Browser SDK Loader Sample</h1>
    <p>Refresh this page and inspect the HTML source for injected browser SDK snippet.</p>
</body>
</html>
"""
    )


urlpatterns = [
    path("", index, name="index"),
]


def main():
    if not settings.configured:
        settings.configure(
            DEBUG=True,
            SECRET_KEY="sample-secret-key",
            ROOT_URLCONF=__name__,
            ALLOWED_HOSTS=["127.0.0.1", "localhost"],
            MIDDLEWARE=[],
            INSTALLED_APPS=[],
        )

    configure_azure_monitor(
        browser_sdk_loader_config={
            "enabled": True,
        }
    )

    execute_from_command_line(["sample", "runserver", "127.0.0.1:8000"])


if __name__ == "__main__":
    main()
