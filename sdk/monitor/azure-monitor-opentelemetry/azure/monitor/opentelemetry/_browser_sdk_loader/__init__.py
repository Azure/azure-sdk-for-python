# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License in the project root for
# license information.
# -------------------------------------------------------------------------

from logging import getLogger

from azure.monitor.opentelemetry._browser_sdk_loader._config import BrowserSDKConfig

_logger = getLogger(__name__)


def setup_snippet_injection(config: BrowserSDKConfig) -> None:
    """Setup snippet injection for supported frameworks.

    :param config: BrowserSDK configuration.
    :type config: BrowserSDKConfig
    :rtype: None
    """
    try:
        # Try to setup Django middleware if Django is available
        _setup_django_injection(config)
        # Future: Add support for other frameworks like Flask, FastAPI, etc.
    except Exception as ex:  # pylint: disable=broad-exception-caught
        _logger.debug("Failed to setup snippet injection: %s", ex, exc_info=True)


def _setup_django_injection(config: BrowserSDKConfig) -> None:
    """Setup Django middleware injection if Django is available and configured.

    This function attempts to automatically register the Application Insights web snippet
    middleware with Django if Django is available and properly configured.

    :param config: BrowserSDK configuration.
    :type config: BrowserSDKConfig
    :rtype: None
    """
    try:
        # Check if Django is available
        try:
            from django.conf import settings  # noqa: F401  # pylint: disable=import-error
        except ImportError:
            _logger.debug("Django not available - skipping Django middleware setup")
            return
        # Check if Django is configured
        try:
            from django.conf import settings  # pylint: disable=import-error

            if not settings.configured:
                _logger.debug("Django not configured - skipping middleware registration")
                return
        except Exception:  # pylint: disable=broad-exception-caught
            _logger.debug("Cannot access Django settings - skipping middleware registration")
            return
        # Try to dynamically register our middleware
        _register_django_middleware(config)
    except Exception as ex:  # pylint: disable=broad-exception-caught
        _logger.debug("Failed to setup Django middleware: %s", ex, exc_info=True)


def _register_django_middleware(config: BrowserSDKConfig) -> None:
    """Register the Application Insights middleware with Django.

    :param config: BrowserSDK configuration.
    :type config: BrowserSDKConfig
    :rtype: None
    """
    try:
        from django.conf import settings  # pylint: disable=import-error

        # Check if our middleware is already in the middleware list
        middleware_path = f"{__name__}.django_middleware.ApplicationInsightsWebSnippetMiddleware"
        if hasattr(settings, "MIDDLEWARE"):
            middleware_list = list(settings.MIDDLEWARE)
            if middleware_path not in middleware_list:
                # Add our middleware to the end of the list
                middleware_list.append(middleware_path)
                settings.MIDDLEWARE = middleware_list
                _logger.debug("Added Application Insights middleware to Django MIDDLEWARE")
        elif hasattr(settings, "MIDDLEWARE_CLASSES"):  # Legacy Django support
            middleware_list = list(settings.MIDDLEWARE_CLASSES)
            if middleware_path not in middleware_list:
                middleware_list.append(middleware_path)
                settings.MIDDLEWARE_CLASSES = middleware_list
                _logger.debug("Added Application Insights middleware to Django MIDDLEWARE_CLASSES")
        # Store configuration globally for the middleware to access
        _store_django_config(config)
    except Exception as ex:  # pylint: disable=broad-exception-caught
        _logger.warning("Failed to register Django middleware: %s", ex, exc_info=True)


def _store_django_config(config: BrowserSDKConfig) -> None:
    """Store the Application Insights configuration for Django middleware access.

    :param config: BrowserSDK configuration.
    :type config: BrowserSDKConfig
    :rtype: None
    """
    try:
        from django.conf import settings  # pylint: disable=import-error

        # Store config in Django settings for middleware to access
        if not hasattr(settings, "AZURE_MONITOR_WEB_SNIPPET_CONFIG"):
            settings.AZURE_MONITOR_WEB_SNIPPET_CONFIG = config
            _logger.debug("Stored Application Insights configuration in Django settings")
    except Exception as ex:  # pylint: disable=broad-exception-caught
        _logger.debug("Failed to store Django configuration: %s", ex, exc_info=True)
