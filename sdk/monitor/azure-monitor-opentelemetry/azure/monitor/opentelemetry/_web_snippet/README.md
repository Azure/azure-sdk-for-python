# Azure Monitor OpenTelemetry Web Snippet Injection

This module provides automatic injection of Application Insights web snippet into HTML responses for Python web applications, starting with Django support.

## Overview

The web snippet injection functionality automatically adds the Application Insights JavaScript SDK to your web pages, enabling client-side telemetry collection including:

- Page views and navigation tracking
- User interactions and click events
- AJAX/Fetch dependency tracking  
- JavaScript exceptions
- Performance metrics
- Custom events and telemetry

## Features

- ✅ **Django Middleware**: Automatic snippet injection for Django applications
- ✅ **Compression Support**: Handles gzip, brotli, and deflate compressed responses
- ✅ **Smart Detection**: Only injects in HTML GET requests, skips if Web SDK already present
- ✅ **Content-Length Updates**: Automatically updates response headers after injection
- ✅ **Configurable**: Extensive configuration options matching Node.js and Java implementations
- ✅ **Framework Detection**: Reports which Python framework was used for snippet injection

## Quick Start

### Django Integration

1. **Add the middleware to your Django settings:**

```python
MIDDLEWARE = [
    # ... other middleware
    'azure.monitor.opentelemetry.DjangoWebSnippetMiddleware',
]
```

2. **Configure Azure Monitor OpenTelemetry with web snippet settings:**

```python
AZURE_MONITOR_OPENTELEMETRY = {
    'connection_string': 'InstrumentationKey=your-key;IngestionEndpoint=https://your-region.in.applicationinsights.azure.com/',
    'web_snippet': {
        'enabled': True,
    }
}
```

3. **Initialize Azure Monitor OpenTelemetry:**

```python
from azure.monitor.opentelemetry import configure_azure_monitor

configure_azure_monitor(
    connection_string='your-connection-string'
)
```

## Configuration Options

### Web Snippet Configuration

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `enabled` | bool | `False` | Enable/disable web snippet injection |
| `connection_string` | str | `None` | Application Insights connection string |

### Django Settings Example

```python
AZURE_MONITOR_OPENTELEMETRY = {
    'connection_string': os.environ.get('APPLICATIONINSIGHTS_CONNECTION_STRING'),
    'web_snippet': {
        'enabled': True,
    }
}
```

## Manual Usage

You can also use the web snippet functionality programmatically:

```python
from azure.monitor.opentelemetry import WebSnippetConfig, WebSnippetInjector

# Create configuration
config = WebSnippetConfig(
    enabled=True,
    connection_string='your-connection-string'
)

# Create injector
injector = WebSnippetInjector(config)

# Check if injection should happen
if injector.should_inject(request.method, response.content_type, response.content):
    # Inject snippet with compression handling
    modified_content, encoding = injector.inject_with_compression(
        response.content,
        response.get('Content-Encoding')
    )
    
    # Update response
    response.content = modified_content
    response['Content-Length'] = len(modified_content)
```

## How It Works

1. **Request Filtering**: Only processes GET requests with HTML content type
2. **Existing SDK Detection**: Checks if Application Insights Web SDK is already present
3. **Content Decompression**: Handles gzip, brotli, and deflate compressed responses
4. **Snippet Injection**: Injects the snippet before `</head>` or `<body>` tags
5. **Content Recompression**: Recompresses content using original encoding
6. **Header Updates**: Updates Content-Length and Content-Encoding headers

## Framework Support Roadmap

- ✅ **Django**: Full support with middleware
- 🚧 **FastAPI**: Planned
- 🚧 **Flask**: Planned
- 🚧 **Tornado**: Planned
- 🚧 **Django REST Framework**: Planned

## Alignment with Other SDKs

This implementation follows the same patterns as:

- **Node.js**: [azure-sdk-for-js monitor-opentelemetry](https://github.com/Azure/azure-sdk-for-js/tree/main/sdk/monitor/monitor-opentelemetry)
- **Java**: [applicationinsights-java browser SDK loader](https://learn.microsoft.com/en-us/azure/azure-monitor/app/java-standalone-config#browser-sdk-loader-preview)
- **.NET**: [.NET web snippet injection](https://github.com/microsoft/ApplicationInsights-dotnet)

## Telemetry and Debugging

### Debug Headers

In Django DEBUG mode, the middleware adds debug headers:

```
X-Azure-Monitor-WebSnippet: injected
```

### Logging

Enable debug logging to see injection details:

```python
import logging
logging.getLogger('azure.monitor.opentelemetry._web_snippet').setLevel(logging.DEBUG)
```

### Statsbeat

The implementation reports framework usage through Statsbeat telemetry to help Microsoft understand usage patterns.

## Limitations and Notes

1. **NPM Dependency**: Currently uses embedded JavaScript snippet. Future versions may integrate with `@microsoft/applicationinsights-web-snippet` npm package.
2. **Django Only**: Initial implementation focuses on Django. Other frameworks coming soon.
3. **GET Requests Only**: Only injects in GET requests serving HTML content.
4. **Compression**: Automatically handles compression/decompression but may impact performance on high-traffic sites.

## Troubleshooting

### Common Issues

1. **Snippet not appearing**: Check that `enabled=True` and connection string is valid
2. **Duplicate telemetry**: Web SDK already present, injection is skipped automatically
3. **Performance impact**: Consider pre-compression hooks for high-traffic applications

### Verification

Check that the snippet was injected by viewing page source and looking for:

```html
<script type="text/javascript">
!function(T,l,y){var S=T.location,k="script"...
```

Or check for the presence of `appInsights` object in browser console.

## Contributing

This is a prototype implementation. Future improvements include:

- Support for additional Python frameworks
- Integration with npm package for snippet generation
- Pre-compression injection hooks
- Advanced configuration options
- Performance optimizations

## References

- [Application Insights JavaScript SDK](https://github.com/microsoft/ApplicationInsights-JS)
- [Web Snippet NPM Package](https://www.npmjs.com/package/@microsoft/applicationinsights-web-snippet)
- [Azure Monitor OpenTelemetry Python Design Guidelines](https://azure.github.io/azure-sdk/python_design.html)
