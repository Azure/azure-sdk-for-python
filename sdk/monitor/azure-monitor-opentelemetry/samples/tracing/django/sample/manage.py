# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

from azure.monitor.opentelemetry import configure_azure_monitor


def main():
    """Run administrative tasks."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sample.settings")

    # Configure Azure monitor collection telemetry pipeline
    # configure_azure_monitor should only be called once in either asgi.py, wsgi.py, or manage.py, depending on startup method.
    # If using manage.py, please remove configure_azure_monitor from asgi.py and wsgi.py
    configure_azure_monitor()

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
