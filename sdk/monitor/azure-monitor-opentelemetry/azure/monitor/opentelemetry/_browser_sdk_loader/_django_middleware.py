# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License in the project root for
# license information.
# -------------------------------------------------------------------------

from typing import Callable, Optional
from logging import getLogger

from ._snippet_injector import WebSnippetInjector
from ._config import WebSnippetConfig

_logger = getLogger(__name__)


class DjangoWebSnippetMiddleware:
    """Django middleware for injecting Browser SDK snippet."""
    
    def __init__(self, get_response: Callable):
        self.get_response = get_response
        self.injector: Optional[WebSnippetInjector] = None
        self._initialized = False
    
    def __call__(self, request):
        """Process the request and inject snippet if appropriate."""
        if not self._initialized:
            self._initialize()
        
        response = self.get_response(request)
        
        if self.injector:
            response = self._process_response(request, response)
        
        return response
    
    def _initialize(self):
        """Initialize the snippet injector with configuration."""
        try:
            # Try to get configuration from Django settings
            config = self._get_web_snippet_config()
            if config and config.enabled:
                self.injector = WebSnippetInjector(config)
                _logger.info("Django Web Snippet Middleware initialized")
            else:
                _logger.debug("Web snippet injection disabled or not configured")
        except Exception as ex:
            _logger.warning("Failed to initialize Django Web Snippet Middleware: %s", ex, exc_info=True)
        finally:
            self._initialized = True
    
    def _get_web_snippet_config(self) -> Optional[WebSnippetConfig]:
        """Get web snippet configuration from Django settings."""
        try:
            # Django is an optional dependency, import conditionally
            from django.conf import settings  # type: ignore
            
            # Check if Azure Monitor OpenTelemetry is configured
            azure_monitor_config = getattr(settings, 'AZURE_MONITOR_OPENTELEMETRY', {})
            web_snippet_config = azure_monitor_config.get('web_snippet', {})
            
            if not web_snippet_config.get('enabled', False):
                return None
            
            # Extract connection string from Azure Monitor config or web snippet config
            connection_string = (
                web_snippet_config.get('connection_string') or 
                azure_monitor_config.get('connection_string') or
                getattr(settings, 'APPLICATIONINSIGHTS_CONNECTION_STRING', None)
            )
            
            if not connection_string:
                _logger.warning("No connection string found for web snippet injection")
                return None
            
            # Create configuration with simplified options
            config = WebSnippetConfig(
                enabled=web_snippet_config.get('enabled', False),
                connection_string=connection_string,
            )
            
            return config
            
        except ImportError:
            _logger.debug("Django not available, cannot configure web snippet middleware")
            return None
        except Exception as ex:
            _logger.warning("Failed to get web snippet configuration from Django settings: %s", ex, exc_info=True)
            return None
    
    def _process_response(self, request, response):
        """Process the response and inject snippet if appropriate."""
        try:
            # Check if injector is available
            if not self.injector:
                return response
            
            # Pre-check basic conditions without decompressing
            if not self.injector.config.enabled:
                return response
                
            # Only inject in GET requests
            if request.method.upper() != "GET":
                return response
                
            # Check content type for HTML
            content_type = response.get('Content-Type', '')
            if not content_type or "html" not in content_type.lower():
                return response
                
            # Get content encoding info
            content_encoding = response.get('Content-Encoding')
            
            # Get original content and try injection (includes SDK detection)
            original_content = response.content
            
            # Inject snippet with compression handling (includes SDK check)
            modified_content, new_encoding = self.injector.inject_with_compression(
                original_content,
                content_encoding
            )
            
            # If content wasn't modified, SDK was already present
            if modified_content == original_content:
                return response
            
            # Update response with modified content
            response.content = modified_content
            
            # Update Content-Length header
            if 'Content-Length' in response:
                response['Content-Length'] = str(len(modified_content))
            
            # Update Content-Encoding if changed
            if new_encoding != content_encoding:
                if new_encoding:
                    response['Content-Encoding'] = new_encoding
                elif 'Content-Encoding' in response:
                    del response['Content-Encoding']
            
            # Add debug headers in development
            if self._is_debug_mode():
                response['X-Azure-Monitor-WebSnippet'] = 'injected'
            
            _logger.debug("Web snippet injected into Django response")
            
        except Exception as ex:
            _logger.warning("Failed to process response for web snippet injection: %s", ex, exc_info=True)
        
        return response
    
    def _is_debug_mode(self) -> bool:
        """Check if Django is in debug mode."""
        try:
            # Django is an optional dependency, import conditionally
            from django.conf import settings  # type: ignore
            return getattr(settings, 'DEBUG', False)
        except ImportError:
            return False
