
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License in the project root for
# license information.
# -------------------------------------------------------------------------

from ._snippet_injector import WebSnippetInjector
from ._config import BrowserSDKLoaderConfig

# Import middleware
from ._django_middleware import DjangoWebSnippetMiddleware

def setup_snippet_injection(connection_string: str, config: dict):
    """Setup snippet injection for supported frameworks."""
    from logging import getLogger
    
    _logger = getLogger(__name__)
    
    try:
        # Try to setup Django middleware if Django is available
        _setup_django_injection(connection_string, config)
        
        # Future: Add support for other frameworks like Flask, FastAPI, etc.
        
    except Exception as ex:  # pylint: disable=broad-except
        _logger.debug("Failed to setup snippet injection: %s", ex, exc_info=True)


def _setup_django_injection(connection_string: str, config: dict):
    """Setup Django middleware injection if Django is available and configured."""
    from logging import getLogger
    
    _logger = getLogger(__name__)
    
    try:
        # Check if Django is available
        try:
            import django
            from django.conf import settings
        except ImportError:
            _logger.debug("Django not available - skipping Django middleware setup")
            return
        
        _logger.debug("Django module available, trying to get settings")
        
        # Check if Django is configured
        if not hasattr(settings, 'MIDDLEWARE'):
            _logger.debug("Django not configured - skipping middleware setup")
            return
            
        # Check if middleware is already in the middleware list
        middleware_list = list(settings.MIDDLEWARE)
        middleware_path = 'azure.monitor.opentelemetry._browser_sdk_loader._django_middleware.DjangoWebSnippetMiddleware'
        
        if middleware_path in middleware_list:
            _logger.debug("DjangoWebSnippetMiddleware already configured")
            return
            
        # Add our middleware to the end of the middleware list
        middleware_list.append(middleware_path)
        settings.MIDDLEWARE = middleware_list
        
        # Configure web snippet settings if not already present
        if not hasattr(settings, 'AZURE_MONITOR_OPENTELEMETRY'):
            settings.AZURE_MONITOR_OPENTELEMETRY = {}
            
        azure_config = settings.AZURE_MONITOR_OPENTELEMETRY
        
        # Set connection string (use config connection string if provided, otherwise main one)
        snippet_connection_string = config.get('connection_string') or connection_string
        if not azure_config.get('connection_string'):
            azure_config['connection_string'] = snippet_connection_string
            
        # Set up web snippet configuration
        if 'web_snippet' not in azure_config:
            azure_config['web_snippet'] = {'enabled': True}
        elif not azure_config['web_snippet'].get('enabled'):
            azure_config['web_snippet']['enabled'] = True
            
        # Merge any additional config
        if config:
            azure_config['web_snippet'].update(config)
            
        _logger.info("DjangoWebSnippetMiddleware automatically configured for web snippet injection")
        
    except ImportError:
        _logger.debug("Django not available - skipping Django middleware setup")
    except Exception as ex:  # pylint: disable=broad-except
        _logger.debug("Failed to setup Django middleware: %s", ex, exc_info=True)
