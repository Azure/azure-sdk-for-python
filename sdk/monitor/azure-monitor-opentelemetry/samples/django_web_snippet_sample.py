# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License in the project root for
# license information.
# -------------------------------------------------------------------------

"""
Django Sample Application demonstrating Azure Monitor OpenTelemetry Web Snippet Injection.

This sample shows how to configure and use the DjangoWebSnippetMiddleware
to automatically inject Application Insights web snippet into HTML responses.
"""

import os
from django.conf import settings
from django.http import HttpResponse
from django.urls import path
from django.core.wsgi import get_wsgi_application

# Configure Django settings
if not settings.configured:
    settings.configure(
        DEBUG=True,
        SECRET_KEY='django-sample-key-for-demo-only',
        ROOT_URLCONF=__name__,
        MIDDLEWARE=[
            'django.middleware.common.CommonMiddleware',
            'azure.monitor.opentelemetry.DjangoWebSnippetMiddleware',  # Add this middleware
        ],
        ALLOWED_HOSTS=['*'],
        
        # Azure Monitor OpenTelemetry Configuration
        AZURE_MONITOR_OPENTELEMETRY={
            'connection_string': os.environ.get(
                'APPLICATIONINSIGHTS_CONNECTION_STRING',
                'InstrumentationKey=00000000-0000-0000-0000-000000000000;IngestionEndpoint=https://westus2-2.in.applicationinsights.azure.com/;LiveEndpoint=https://westus2.livediagnostics.monitor.azure.com/'
            ),
            'web_snippet': {
                'enabled': True,
            }
        }
    )


def home_view(request):
    """Sample home page view."""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Azure Monitor OpenTelemetry - Django Sample</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .container { max-width: 800px; margin: 0 auto; }
            .info { background: #f0f8ff; padding: 20px; border-radius: 8px; margin: 20px 0; }
            .button { background: #0078d4; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }
            .button:hover { background: #106ebe; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Azure Monitor OpenTelemetry - Django Sample</h1>
            
            <div class="info">
                <h3>🎯 Web Snippet Injection Demo</h3>
                <p>This page demonstrates automatic injection of Application Insights web snippet into Django responses.</p>
                <p>The middleware automatically detects HTML responses and injects the web snippet before the closing &lt;/head&gt; tag.</p>
            </div>
            
            <h2>Sample User Interactions</h2>
            <p>Try these interactions to see telemetry in Application Insights:</p>
            
            <button class="button" onclick="trackCustomEvent()">Track Custom Event</button>
            <button class="button" onclick="trackException()">Track Exception</button>
            <button class="button" onclick="makeAjaxCall()">Make AJAX Call</button>
            
            <h2>What's Being Tracked</h2>
            <ul>
                <li>Page views and navigation</li>
                <li>User clicks and interactions</li>
                <li>AJAX calls and dependencies</li>
                <li>JavaScript exceptions</li>
                <li>Performance metrics</li>
            </ul>
            
            <div class="info">
                <strong>Note:</strong> The Application Insights web snippet is automatically injected by the 
                <code>DjangoWebSnippetMiddleware</code>. Check the page source to see the injected script.
            </div>
        </div>
        
        <script>
            function trackCustomEvent() {
                if (typeof appInsights !== 'undefined') {
                    appInsights.trackEvent({name: 'ButtonClick', properties: {button: 'CustomEvent'}});
                    alert('Custom event tracked!');
                } else {
                    alert('Application Insights not loaded yet. Please wait and try again.');
                }
            }
            
            function trackException() {
                if (typeof appInsights !== 'undefined') {
                    try {
                        throw new Error('Sample exception for testing');
                    } catch (e) {
                        appInsights.trackException({exception: e});
                        alert('Exception tracked!');
                    }
                } else {
                    alert('Application Insights not loaded yet. Please wait and try again.');
                }
            }
            
            function makeAjaxCall() {
                fetch('/api/sample')
                    .then(response => response.json())
                    .then(data => {
                        alert('AJAX call completed. Check Application Insights for dependency tracking.');
                    })
                    .catch(error => {
                        console.error('AJAX error:', error);
                    });
            }
        </script>
    </body>
    </html>
    """
    return HttpResponse(html_content, content_type='text/html')


def api_sample_view(request):
    """Sample API endpoint for AJAX testing."""
    return HttpResponse('{"message": "Hello from Django API", "status": "success"}', 
                       content_type='application/json')


def json_view(request):
    """Sample JSON response (should not have snippet injected)."""
    return HttpResponse('{"message": "This is JSON, no snippet should be injected"}', 
                       content_type='application/json')


# URL configuration
urlpatterns = [
    path('', home_view, name='home'),
    path('api/sample', api_sample_view, name='api_sample'),
    path('json', json_view, name='json'),
]


# WSGI application
application = get_wsgi_application()


if __name__ == '__main__':
    """Run the sample application."""
    import sys
    
    print("🚀 Starting Django Sample with Azure Monitor OpenTelemetry Web Snippet Injection")
    print("📍 URL: http://localhost:8000")
    print("🔧 Configuration:")
    print(f"   - Web Snippet Enabled: {settings.AZURE_MONITOR_OPENTELEMETRY['web_snippet']['enabled']}")
    print(f"   - Connection String: {settings.AZURE_MONITOR_OPENTELEMETRY['connection_string'][:50]}...")
    print("\n💡 Open the browser and check the page source to see the injected Application Insights snippet.")
    print("⚠️  Note: This is a minimal Django setup for demonstration purposes only.")
    
    # Import and configure Azure Monitor OpenTelemetry
    try:
        from azure.monitor.opentelemetry import configure_azure_monitor
        configure_azure_monitor(
            connection_string=settings.AZURE_MONITOR_OPENTELEMETRY['connection_string']
        )
        print("✅ Azure Monitor OpenTelemetry configured successfully")
    except ImportError:
        print("❌ Azure Monitor OpenTelemetry not available. Install with: pip install azure-monitor-opentelemetry")
        sys.exit(1)
    
    # Run development server
    from django.core.management import execute_from_command_line
    execute_from_command_line(['manage.py', 'runserver'])
