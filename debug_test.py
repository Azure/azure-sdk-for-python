#!/usr/bin/env python3
"""Simple test to debug the Django middleware issue"""

from unittest.mock import MagicMock

# Simulate what the test does
settings_mock = MagicMock()
settings_mock.MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.common.CommonMiddleware',
]

print("Initial MIDDLEWARE:", settings_mock.MIDDLEWARE)

# Simulate what the function does
middleware_list = list(settings_mock.MIDDLEWARE)
middleware_path = 'azure.monitor.opentelemetry._web_snippet._django_middleware.DjangoWebSnippetMiddleware'

print("middleware_list before append:", middleware_list)
middleware_list.append(middleware_path)
print("middleware_list after append:", middleware_list)

settings_mock.MIDDLEWARE = middleware_list
print("settings_mock.MIDDLEWARE after assignment:", settings_mock.MIDDLEWARE)
print("Expected middleware in settings_mock.MIDDLEWARE:", middleware_path in settings_mock.MIDDLEWARE)
