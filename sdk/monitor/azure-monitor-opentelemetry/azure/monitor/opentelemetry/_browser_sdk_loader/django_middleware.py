# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License in the project root for
# license information.
# -------------------------------------------------------------------------

from typing import Optional, Callable, Any, Union
from logging import getLogger

try:
    from django.http import HttpRequest, HttpResponse  # type: ignore
    from django.utils.deprecation import MiddlewareMixin  # type: ignore
    DJANGO_AVAILABLE = True
except ImportError:
    # Define stub classes when Django is not available
    HttpRequest = Any
    HttpResponse = Any
    MiddlewareMixin = object
    DJANGO_AVAILABLE = False

from .snippet_injector import WebSnippetInjector
from ._config import BrowserSDKConfig

_logger = getLogger(__name__)


class ApplicationInsightsWebSnippetMiddleware(MiddlewareMixin):
    """Django middleware for injecting Application Insights web snippet into HTML responses.

    This middleware automatically injects the Application Insights JavaScript SDK snippet
    into HTML responses from Django applications.

    :param get_response: Django's get_response callable.
    :type get_response: Callable
    """

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        """Initialize the middleware.

        :param get_response: Django's get_response callable.
        :type get_response: Callable[[HttpRequest], HttpResponse]
        :rtype: None
        """
        super().__init__(get_response)
        self.get_response = get_response
        self._injector: Optional[WebSnippetInjector] = None
        if not DJANGO_AVAILABLE:
            _logger.warning("Django not available - ApplicationInsightsWebSnippetMiddleware will not function")
            return

        # Auto-configure from Django settings if available
        self._auto_configure_from_settings()

    def __call__(self, request: HttpRequest) -> HttpResponse:
        """Process the request through the middleware.

        :param request: Django HTTP request object.
        :type request: HttpRequest
        :return: Django HTTP response object with potentially injected snippet.
        :rtype: HttpResponse
        """
        response = self.get_response(request)
        return self.process_response(request, response)

    def process_response(self, request: HttpRequest, response: HttpResponse) -> HttpResponse:
        """Process the response to inject the Application Insights snippet if appropriate.

        :param request: Django HTTP request object.
        :type request: HttpRequest
        :param response: Django HTTP response object to potentially modify.
        :type response: HttpResponse
        :return: Django HTTP response object with potentially injected snippet.
        :rtype: HttpResponse
        """
        if not DJANGO_AVAILABLE or not self._injector:
            return response
        try:
            # Get response details
            content_type = response.get('Content-Type', '')
            content_encoding = response.get('Content-Encoding')
            # Check if we should inject the snippet
            if not self._injector.should_inject(
                request.method,
                content_type,
                response.content,
                content_encoding
            ):
                return response
            # Inject the snippet with compression handling
            modified_content, new_encoding = self._injector.inject_with_compression(
                response.content,
                content_encoding
            )
            # Update response with modified content
            response.content = modified_content
            if new_encoding and new_encoding != content_encoding:
                response['Content-Encoding'] = new_encoding
            # Update content length if it changed
            response['Content-Length'] = str(len(modified_content))
        except Exception as ex:
            _logger.warning("Failed to inject Application Insights snippet: %s", ex, exc_info=True)
        return response

    def configure(self, config: Union[BrowserSDKConfig, dict, str], legacy_config: Optional[dict] = None) -> None:  # pylint: disable=unused-argument
        """Configure the middleware with Application Insights settings.

        :param config: Configuration object, dict, or connection string.
        :type config: Union[BrowserSDKConfig, dict, str]
        :param legacy_config: Legacy configuration options (for backward compatibility).
        :type legacy_config: dict or None
        :rtype: None
        """
        try:
            if isinstance(config, BrowserSDKConfig):
                # Use BrowserSDKConfig object directly
                snippet_config = config
            elif isinstance(config, dict):
                # Create BrowserSDKConfig from dictionary
                snippet_config = BrowserSDKConfig(
                    enabled=config.get('enabled', True),
                    connection_string=config.get('connection_string', '')
                )
            elif isinstance(config, str):
                # Legacy mode: config is connection string
                snippet_config = BrowserSDKConfig(
                    enabled=True,
                    connection_string=config
                )
            else:
                _logger.error("Invalid config type provided to configure(): %s", type(config))
                return

            self._injector = WebSnippetInjector(snippet_config)
        except Exception as ex:
            _logger.error("Failed to configure middleware: %s", ex, exc_info=True)

    def _auto_configure_from_settings(self) -> None:
        """Auto-configure the middleware from Django settings if available.

        :rtype: None
        """
        try:
            from django.conf import settings

            # Look for configuration in Django settings
            if hasattr(settings, 'AZURE_MONITOR_WEB_SNIPPET_CONFIG'):
                config = settings.AZURE_MONITOR_WEB_SNIPPET_CONFIG

                if isinstance(config, (dict, BrowserSDKConfig)):
                    # Pass the configuration to configure method (handles both dict and BrowserSDKConfig)
                    self.configure(config)
                    _logger.debug("Auto-configured Application Insights middleware from Django settings")
                else:
                    _logger.debug("Invalid AZURE_MONITOR_WEB_SNIPPET_CONFIG format in Django settings")
            else:
                _logger.debug("No AZURE_MONITOR_WEB_SNIPPET_CONFIG found in Django settings")

        except Exception as ex:
            _logger.debug("Failed to auto-configure from Django settings: %s", ex, exc_info=True)
