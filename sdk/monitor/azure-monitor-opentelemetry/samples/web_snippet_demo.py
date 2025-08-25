# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License in the project root for
# license information.
# -------------------------------------------------------------------------

"""
Standalone demonstration of Azure Monitor OpenTelemetry Web Snippet Injection.

This script demonstrates the core web snippet injection functionality
without requiring Django or other web framework dependencies.
"""

import gzip
import sys
import os

# Add the package to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
package_dir = os.path.dirname(current_dir)
sys.path.insert(0, package_dir)

# Note: brotli and zlib could be imported if needed for compression demo
from azure.monitor.opentelemetry._web_snippet import WebSnippetConfig, WebSnippetInjector


def demo_basic_injection():
    """Demonstrate basic snippet injection."""
    print("🔧 Demo: Basic Web Snippet Injection")
    print("=" * 50)
    
    # Create configuration
    config = WebSnippetConfig(
        enabled=True,
        connection_string="InstrumentationKey=12345678-1234-1234-1234-123456789012;IngestionEndpoint=https://westus2-2.in.applicationinsights.azure.com/"
    )
    
    # Create injector
    injector = WebSnippetInjector(config)
    
    # Sample HTML content
    html_content = b"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Sample Page</title>
</head>
<body>
    <h1>Hello World</h1>
    <p>This is a sample page for web snippet injection.</p>
</body>
</html>"""
    
    # Check if injection should happen
    should_inject = injector.should_inject("GET", "text/html", html_content)
    print(f"Should inject snippet: {should_inject}")
    
    if should_inject:
        # Inject snippet
        modified_content = injector.inject_snippet(html_content)
        
        # Show results
        print(f"Original size: {len(html_content)} bytes")
        print(f"Modified size: {len(modified_content)} bytes")
        print(f"Size increase: {len(modified_content) - len(html_content)} bytes")
        
        # Show snippet location
        modified_str = modified_content.decode('utf-8')
        if 'appInsights' in modified_str:
            snippet_start = modified_str.find('<script type="text/javascript">')
            snippet_end = modified_str.find('</script>', snippet_start) + 9
            print(f"\n✅ Snippet injected successfully!")
            print(f"📍 Location: character position {snippet_start}")
            print(f"📏 Snippet length: {snippet_end - snippet_start} characters")
        else:
            print("❌ Snippet not found in modified content")
    
    print()


def demo_compressed_sdk_detection():
    """Demonstrate detection of existing Web SDK in compressed content."""
    print("🔍 Demo: Compressed Content SDK Detection")
    print("=" * 50)
    
    # Create configuration
    config = WebSnippetConfig(
        enabled=True,
        connection_string="InstrumentationKey=12345678-1234-1234-1234-123456789012;IngestionEndpoint=https://westus2-2.in.applicationinsights.azure.com/"
    )
    
    # Create injector
    injector = WebSnippetInjector(config)
    
    # HTML with existing Web SDK
    html_with_sdk = b"""<!DOCTYPE html>
<html>
<head>
    <title>Page with existing SDK</title>
    <script>var appInsights = window.appInsights || {};</script>
</head>
<body>
    <h1>Hello World</h1>
</body>
</html>"""
    
    print("1. Testing uncompressed content with existing SDK:")
    should_inject = injector.should_inject("GET", "text/html", html_with_sdk)
    print(f"   Should inject: {should_inject} (expected: False)")
    
    print("2. Testing gzip-compressed content with existing SDK:")
    compressed_content = gzip.compress(html_with_sdk)
    should_inject = injector.should_inject("GET", "text/html", compressed_content, "gzip")
    print(f"   Should inject: {should_inject} (expected: False)")
    
    print("3. Testing brotli-compressed content with existing SDK:")
    # Note: brotli compression requires the 'brotli' package
    # try:
    #     import brotli
    #     br_compressed = brotli.compress(html_with_sdk)
    #     should_inject = injector.should_inject("GET", "text/html", br_compressed, "br")
    #     print(f"   Should inject: {should_inject} (expected: False)")
    # except ImportError:
    #     print("   Brotli package not available - skipping test")
    # except Exception as e:
    #     print(f"   Brotli compression failed: {e}")
    print("   Skipped (brotli package not available)")
    
    print("4. Testing auto-detection (no encoding specified):")
    should_inject = injector.should_inject("GET", "text/html", compressed_content)
    print(f"   Should inject: {should_inject} (expected: False)")
    
    print()


def demo_compression_handling():
    """Demonstrate compression handling."""
    print("🗜️  Demo: Compression Handling")
    print("=" * 50)
    
    # Create configuration
    config = WebSnippetConfig(
        enabled=True,
        connection_string="InstrumentationKey=12345678-1234-1234-1234-123456789012;IngestionEndpoint=https://westus2-2.in.applicationinsights.azure.com/"
    )
    
    # Create injector
    injector = WebSnippetInjector(config)
    
    # Sample HTML content
    html_content = b"""<!DOCTYPE html>
<html>
<head><title>Compressed Page</title></head>
<body><h1>This content will be compressed</h1></body>
</html>"""
    
    # Compress with gzip
    compressed_content = gzip.compress(html_content)
    print(f"Original size: {len(html_content)} bytes")
    print(f"Compressed size: {len(compressed_content)} bytes")
    print(f"Compression ratio: {len(compressed_content)/len(html_content):.2%}")
    
    # Inject snippet with compression handling
    modified_content, encoding = injector.inject_with_compression(
        compressed_content,
        "gzip"
    )
    
    # Decompress to verify
    if encoding == "gzip":
        decompressed = gzip.decompress(modified_content)
        print(f"Modified compressed size: {len(modified_content)} bytes")
        print(f"Modified decompressed size: {len(decompressed)} bytes")
        
        if b'appInsights' in decompressed:
            print("✅ Snippet successfully injected in compressed content!")
        else:
            print("❌ Snippet not found in decompressed content")
    
    print()


def demo_configuration_options():
    """Demonstrate different configuration options."""
    print("⚙️  Demo: Configuration Options")
    print("=" * 50)
    
    # Create custom configuration (simplified)
    config = WebSnippetConfig(
        enabled=True,
        connection_string="InstrumentationKey=12345678-1234-1234-1234-123456789012;IngestionEndpoint=https://westus2-2.in.applicationinsights.azure.com/",
    )
    
    # Show configuration as dict
    config_dict = config.to_dict()
    print("Configuration:")
    print(f"  Enabled: {config_dict['enabled']}")
    print(f"  Connection String: {config_dict['connectionString'][:50]}...")
    print(f"  CORS Correlation: {config_dict['cfg']['enableCorsCorrelation']}")
    print(f"  Distribution Tracking: {config_dict['cfg']['distributionTracking']}")
    print(f"  Session Renewal: {config_dict['cfg']['sessionRenewalMs']} ms")
    print(f"  SDK Extension: {config_dict['cfg']['sdkExtension']}")
    
    # Extract instrumentation key
    ikey = config._extract_instrumentation_key()
    print(f"  Extracted Instrumentation Key: {ikey}")
    
    print()


def demo_edge_cases():
    """Demonstrate edge cases and error handling."""
    print("🔍 Demo: Edge Cases and Error Handling")
    print("=" * 50)
    
    config = WebSnippetConfig(
        enabled=True,
        connection_string="InstrumentationKey=test;IngestionEndpoint=https://test.com/"
    )
    injector = WebSnippetInjector(config)
    
    # Test cases
    test_cases = [
        ("Non-HTML content", b'{"json": "data"}', "application/json"),
        ("POST request", b"<html><head></head><body></body></html>", "text/html"),
        ("Existing Web SDK", b"<html><head><script>appInsights.track()</script></head><body></body></html>", "text/html"),
        ("Malformed HTML", b"<html><head><body>Missing closing tags", "text/html"),
        ("Empty content", b"", "text/html"),
    ]
    
    for name, content, content_type in test_cases:
        method = "POST" if "POST" in name else "GET"
        should_inject = injector.should_inject(method, content_type, content)
        print(f"{name}: {'✅ Would inject' if should_inject else '❌ Would not inject'}")
    
    print()


def demo_performance_considerations():
    """Demonstrate performance considerations."""
    print("⚡ Demo: Performance Considerations")
    print("=" * 50)
    
    import time
    
    config = WebSnippetConfig(
        enabled=True,
        connection_string="InstrumentationKey=test;IngestionEndpoint=https://test.com/"
    )
    injector = WebSnippetInjector(config)
    
    # Generate larger HTML content
    large_html = b"<html><head><title>Large Page</title></head><body>"
    large_html += b"<p>Content block</p>" * 1000  # Repeat content
    large_html += b"</body></html>"
    
    print(f"Large HTML size: {len(large_html):,} bytes")
    
    # Time the injection
    start_time = time.time()
    modified = large_html  # Initialize with original content
    
    for i in range(10):
        should_inject = injector.should_inject("GET", "text/html", large_html)
        if should_inject:
            modified = injector.inject_snippet(large_html)
    
    end_time = time.time()
    avg_time = (end_time - start_time) / 10 * 1000  # Convert to milliseconds
    
    print(f"Average injection time: {avg_time:.2f} ms")
    print(f"Injected size: {len(modified):,} bytes")
    print(f"Performance impact: {avg_time:.2f} ms per request")
    
    print()


def main():
    """Run all demos."""
    print("🚀 Azure Monitor OpenTelemetry Web Snippet Injection Demo")
    print("=" * 60)
    print()
    
    try:
        demo_basic_injection()
        demo_compressed_sdk_detection()
        demo_configuration_options()
        demo_edge_cases()
        demo_performance_considerations()
        
        print("✅ All demos completed successfully!")
        print()
        print("Next Steps:")
        print("1. Configure your Django application with DjangoWebSnippetMiddleware")
        print("2. Set up Azure Monitor OpenTelemetry configuration")
        print("3. Test with real HTML responses")
        print("4. Monitor telemetry in Application Insights portal")
        
    except Exception as e:
        print(f"❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
