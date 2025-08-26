# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License in the project root for
# license information.
# -------------------------------------------------------------------------

import gzip
import re
from typing import Optional, Dict, Any, Union
from logging import getLogger

# Optional compression libraries
try:
    import brotli
    HAS_BROTLI = True
except ImportError:
    HAS_BROTLI = False

try:
    import zlib
    HAS_ZLIB = True
except ImportError:
    HAS_ZLIB = False

from ._config import WebSnippetConfig

_logger = getLogger(__name__)

# Web SDK snippet template - this would ideally be sourced from @microsoft/applicationinsights-web-snippet npm package
_WEB_SDK_SNIPPET_TEMPLATE = '''<script type="text/javascript">
!function(T,l,y){var S=T.location,k="script",D="instrumentationKey",C="ingestionendpoint",I="disableExceptionTracking",E="ai.device.",b="toLowerCase",w="crossOrigin",N="POST",e="appInsightsSDK",t=y.name||"appInsights";(y.name||T[e])&&(T[e]=t);var n=T[t]||function(d){var g=!1,f=!1,m={initialize:!0,queue:[],sv:"5",version:2,config:d};function v(e,t){var n={},a="Browser";return n[E+"id"]=a[b](),n[E+"type"]=a,n["ai.operation.name"]=S&&S.pathname||"_unknown_",n["ai.internal.sdkVersion"]="javascript:snippet_"+(m.sv||m.version),{time:function(){var a=new Date;function b(e){var t=""+e;return 1===t.length&&(t="0"+t),t}return a.getUTCFullYear()+"-"+b(1+a.getUTCMonth())+"-"+b(a.getUTCDate())+"T"+b(a.getUTCHours())+":"+b(a.getUTCMinutes())+":"+b(a.getUTCSeconds())+"."+((a.getUTCMilliseconds()/1e3).toFixed(3)+"").slice(2,5)+"Z"}(),iKey:e,name:"Microsoft.ApplicationInsights."+t.replace(/\\s/g,"")+"."+v,sampleRate:100,tags:n,data:{baseData:{ver:2}}}}var h=d.url||y.src;if(h){function a(e){var t,n,a,i,r,o,s,c,u,p,l;g=!0,m.queue=[],f||(f=!0,t=h,s=function(){var e={},t=d.connectionString;if(t)for(var n=t.split(";"),a=0;a<n.length;a++){var i=n[a].split("=");2===i.length&&(e[i[0][b]()]=i[1])}if(!e[C]){var r=e.endpointsuffix,o=r?e.location:null;e[C]="https://"+(o?o+".":"")+"dc."+(r||"services.visualstudio.com")}return e}(),c=s[D]||d[D]||"",u=s[C],p=u?u+"/v2/track":d.endpointUrl,(l=[]).push((n="SDK LOAD Failure: Failed to load Application Insights SDK script (See stack for details)",a=t,i=p,(o=(r=v(c,"Exception")).data).baseType="ExceptionData",o.baseData.exceptions=[{typeName:"SDKLoadFailed",message:n.replace(/\\./g,"-"),hasFullStack:!1,stack:n+"\\nSnippet failed to load ["+a+"] -- Telemetry is disabled\\nHelp Link: https://go.microsoft.com/fwlink/?linkid=2128109\\nHost: "+(S&&S.pathname||"_unknown_")+"\\nEndpoint: "+i,parsedStack:[]}],r)),l.push(function(e,t,n,a){var i=v(c,"Message"),r=i.data;r.baseType="MessageData";var o=r.baseData;return o.message='AI (Internal): 99 message:"'+("SDK LOAD Failure: Failed to load Application Insights SDK script (See stack for details) ("+n+")").replace(/\\"/g,"")+'"',o.properties={endpoint:a},i}(0,0,t,p)),function(e,t){if(JSON){var n=T.fetch;if(n&&!y.useXhr)n(t,{method:N,body:JSON.stringify(e),mode:"cors"});else if(XMLHttpRequest){var a=new XMLHttpRequest;a.open(N,t),a.setRequestHeader("Content-type","application/json"),a.send(JSON.stringify(e))}}}(l,p))}function i(e,t){f||setTimeout(function(){!t&&m.core||a()},500)}var e=function(){var n=l.createElement(k);n.src=h;var e=y[w];return!e&&""!==e||"undefined"==n[w]||(n[w]=e),n.onload=i,n.onerror=a,n.onreadystatechange=function(e,t){"loaded"!==n.readyState&&"complete"!==n.readyState||i(0,t)},n}();y.ld<0?l.getElementsByTagName("head")[0].appendChild(e):setTimeout(function(){l.getElementsByTagName(k)[0].parentNode.insertBefore(e,l.getElementsByTagName(k)[0])},y.ld||0)}try{m.cookie=l.cookie}catch(p){}function t(e){for(;e.length;)!function(t){m[t]=function(){var e=arguments;g||m.queue.push(function(){m[t].apply(m,e)})}}(e.pop())}var n="track",r="TrackPage",o="TrackEvent";t([n+"Event",n+"PageView",n+"Exception",n+"Trace",n+"DependencyData",n+"Metric",n+"PageViewPerformance","start"+r,"stop"+r,"start"+o,"stop"+o,"addTelemetryInitializer","setAuthenticatedUserContext","clearAuthenticatedUserContext","flush"]),m.SeverityLevel={Verbose:0,Information:1,Warning:2,Error:3,Critical:4};var s=(d.extensionConfig||{}).ApplicationInsightsAnalytics||{};if(!0!==d[I]&&!0!==s[I]){var c="onerror";t(["_"+c]);var u=T[c];T[c]=function(e,t,n,a,i){var r=u&&u(e,t,n,a,i);return!0!==r&&m["_"+c]({message:e,url:t,lineNumber:n,columnNumber:a,error:i}),r},d.autoExceptionInstrumented=!0}return m}(y.cfg);function a(){y.onInit&&y.onInit(n)}(T[t]=n).queue&&0===n.queue.length?(n.queue.push(a),n.trackPageView({})):a()}(window,document,{
src: "https://js.monitor.azure.com/scripts/b/ai.2.min.js",
cfg: {CONFIG_PLACEHOLDER}
});
</script>'''


class WebSnippetInjector:
    """Handles injection of Application Insights web snippet into HTML responses."""
    
    def __init__(self, config: WebSnippetConfig):
        self.config = config
        self._web_sdk_snippet_cache: Optional[str] = None
        self._decompressed_content_cache: Optional[bytes] = None
        self._cache_key: Optional[tuple] = None
        
        # Regex patterns for detecting existing Web SDK
        self._existing_sdk_patterns = [
            re.compile(r'appInsights', re.IGNORECASE),
            re.compile(r'ApplicationInsights', re.IGNORECASE),
            re.compile(r'ai\.2\.min\.js', re.IGNORECASE),
            re.compile(r'js\.monitor\.azure\.com', re.IGNORECASE),
        ]
    
    def should_inject(self, request_method: str, content_type: Optional[str], content: bytes, content_encoding: Optional[str] = None) -> bool:
        """Determine if snippet should be injected into this response."""
        if not self.config.enabled:
            return False
            
        # Only inject in GET requests
        if request_method.upper() != "GET":
            return False
            
        # Check content type for HTML
        if not content_type or "html" not in content_type.lower():
            return False
        
        # Get decompressed content once and cache it for reuse
        decompressed_content = self._get_decompressed_content(content, content_encoding)
            
        # Check if Web SDK is already present using cached decompressed content
        if self._has_existing_web_sdk_from_decompressed(decompressed_content):
            _logger.debug("Web SDK already detected in HTML, skipping injection")
            return False
            
        return True
    
    def inject_snippet(self, content: bytes, encoding: str = "utf-8") -> bytes:
        """Inject the web snippet into HTML content."""
        try:
            # Decode content
            html_content = content.decode(encoding)
            
            # Generate snippet
            snippet = self._get_web_snippet()
            
            # Find insertion point (before </head> or <body>)
            insertion_point = self._find_insertion_point(html_content)
            if insertion_point == -1:
                _logger.warning("Could not find suitable insertion point for web snippet")
                return content
                
            # Insert snippet
            modified_html = (
                html_content[:insertion_point] + 
                snippet + 
                html_content[insertion_point:]
            )
            
            return modified_html.encode(encoding)
            
        except Exception as ex:
            _logger.warning("Failed to inject web snippet: %s", ex, exc_info=True)
            return content
    
    def inject_with_compression(
        self, 
        content: bytes, 
        content_encoding: Optional[str] = None,
        encoding: str = "utf-8"
    ) -> tuple[bytes, Optional[str]]:
        """Inject snippet handling compression/decompression efficiently using cached decompressed content."""
        try:
            # Use cached decompressed content if available, otherwise decompress
            decompressed_content = self._get_decompressed_content(content, content_encoding)
            
            # Auto-detect encoding if not specified and content was compressed
            detected_encoding = content_encoding
            if not content_encoding and decompressed_content != content:
                # Content was decompressed, try to detect which format was used
                for enc in ["gzip", "br", "deflate"]:
                    try:
                        test_compressed = self._compress_content(decompressed_content, enc)
                        if test_compressed == content:
                            detected_encoding = enc
                            break
                    except Exception:
                        continue
            
            # Check for existing SDK using cached decompressed content
            if self._has_existing_web_sdk_from_decompressed(decompressed_content):
                _logger.debug("Web SDK already detected in HTML, skipping injection")
                return content, content_encoding
            
            # Inject snippet into decompressed content
            modified_content = self.inject_snippet(decompressed_content, encoding)
            
            # Recompress if original was compressed
            if detected_encoding:
                compressed_content = self._compress_content(modified_content, detected_encoding)
                return compressed_content, detected_encoding
            else:
                return modified_content, None
                
        except Exception as ex:
            _logger.warning("Failed to inject snippet with compression handling: %s", ex, exc_info=True)
            return content, content_encoding
    
    def _get_web_snippet(self) -> str:
        """Generate the web snippet with configuration."""
        if self._web_sdk_snippet_cache is None:
            config_dict = self.config.to_dict()
            config_json = self._dict_to_js_object(config_dict.get("cfg", {}))
            self._web_sdk_snippet_cache = _WEB_SDK_SNIPPET_TEMPLATE.replace(
                "{CONFIG_PLACEHOLDER}", 
                config_json
            )
        return self._web_sdk_snippet_cache
    
    def _get_decompressed_content(self, content: bytes, content_encoding: Optional[str] = None) -> bytes:
        """Get decompressed content with caching to avoid redundant decompression."""
        # Fast path: if no encoding specified and content doesn't look compressed, return as-is
        if not content_encoding:
            # Quick check for compression headers to avoid unnecessary processing
            if not self._appears_compressed(content):
                return content
        
        # For compressed content or when encoding is specified, use caching
        cache_key = (hash(content), content_encoding)
        
        # Return cached result if available
        if self._cache_key == cache_key and self._decompressed_content_cache is not None:
            return self._decompressed_content_cache
        
        # Decompress content based on encoding header
        decompressed_content = self._decompress_content(content, content_encoding)
        
        # If no encoding was specified and content wasn't decompressed, try auto-detection
        if not content_encoding and decompressed_content == content:
            for encoding in ["gzip", "br", "deflate"]:
                try:
                    test_decompressed = self._decompress_content(content, encoding)
                    if test_decompressed != content:  # Successfully decompressed
                        decompressed_content = test_decompressed
                        break
                except Exception:
                    continue
        
        # Cache the result only if we actually did decompression work
        if content_encoding or decompressed_content != content:
            self._cache_key = cache_key
            self._decompressed_content_cache = decompressed_content
        
        return decompressed_content
    
    def _appears_compressed(self, content: bytes) -> bool:
        """Quick check if content appears to be compressed based on magic numbers."""
        if len(content) < 3:
            return False
        
        # Check for common compression magic numbers
        # Gzip: starts with 0x1f 0x8b
        if content.startswith(b'\x1f\x8b'):
            return True
        
        # Brotli: no reliable magic number, but check for common patterns
        # (Brotli detection is harder without trying to decompress)
        
        # zlib/deflate: starts with 0x78 followed by various values
        if content[0] == 0x78 and content[1] in (0x01, 0x5E, 0x9C, 0xDA):
            return True
            
        return False
    
    def _clear_decompression_cache(self) -> None:
        """Clear the decompressed content cache."""
        self._decompressed_content_cache = None
        self._cache_key = None
    
    def _has_existing_web_sdk(self, content: bytes, content_encoding: Optional[str] = None) -> bool:
        """Check if Web SDK is already present in the HTML, handling compressed content."""
        try:
            # Decompress content once based on encoding
            decompressed_content = self._decompress_content(content, content_encoding)
            
            # If no encoding was specified and content wasn't decompressed, try auto-detection
            if not content_encoding and decompressed_content == content:
                for encoding in ["gzip", "br", "deflate"]:
                    try:
                        test_decompressed = self._decompress_content(content, encoding)
                        if test_decompressed != content:  # Successfully decompressed
                            decompressed_content = test_decompressed
                            break
                    except Exception:
                        continue
            
            return self._has_existing_web_sdk_from_decompressed(decompressed_content)
                    
        except Exception:
            return False
    
    def _has_existing_web_sdk_from_decompressed(self, decompressed_content: bytes) -> bool:
        """Check if Web SDK is already present in decompressed HTML content."""
        try:
            # Convert decompressed content to string and check for patterns
            content_str = decompressed_content.decode("utf-8", errors="ignore")
            return any(pattern.search(content_str) for pattern in self._existing_sdk_patterns)
        except Exception:
            return False
    
    def _find_insertion_point(self, html_content: str) -> int:
        """Find the best insertion point for the snippet."""
        # Try to insert before </head>
        head_end = html_content.lower().find("</head>")
        if head_end != -1:
            return head_end
            
        # Fallback: insert before <body>
        body_start = html_content.lower().find("<body")
        if body_start != -1:
            return body_start
            
        # Last resort: insert at the beginning of <html>
        html_start = html_content.lower().find("<html")
        if html_start != -1:
            return html_start
            
        return -1
    
    def _decompress_content(self, content: bytes, encoding: Optional[str]) -> bytes:
        """Decompress content based on encoding."""
        if not encoding:
            return content
            
        try:
            if encoding.lower() == "gzip":
                return gzip.decompress(content)
            elif encoding.lower() == "br":
                if not HAS_BROTLI:
                    _logger.warning("brotli library not available for decompression")
                    return content
                return brotli.decompress(content)
            elif encoding.lower() == "deflate":
                if not HAS_ZLIB:
                    _logger.warning("zlib library not available for decompression")
                    return content
                return zlib.decompress(content)
            else:
                return content
        except Exception as ex:
            _logger.warning("Failed to decompress content with encoding %s: %s", encoding, ex)
            return content
    
    def _compress_content(self, content: bytes, encoding: str) -> bytes:
        """Compress content using specified encoding."""
        try:
            if encoding.lower() == "gzip":
                return gzip.compress(content)
            elif encoding.lower() == "br":
                if not HAS_BROTLI:
                    _logger.warning("brotli library not available for compression")
                    return content
                return brotli.compress(content)
            elif encoding.lower() == "deflate":
                if not HAS_ZLIB:
                    _logger.warning("zlib library not available for compression")
                    return content
                return zlib.compress(content)
            else:
                return content
        except Exception as ex:
            _logger.warning("Failed to compress content with encoding %s: %s", encoding, ex)
            return content
    
    def _dict_to_js_object(self, obj: Dict[str, Any]) -> str:
        """Convert Python dict to JavaScript object literal."""
        def format_value(value):
            if isinstance(value, str):
                return f'"{value}"'
            elif isinstance(value, bool):
                return "true" if value else "false"
            elif isinstance(value, (int, float)):
                return str(value)
            elif isinstance(value, dict):
                return self._dict_to_js_object(value)
            else:
                return f'"{str(value)}"'
        
        items = []
        for key, value in obj.items():
            items.append(f'{key}: {format_value(value)}')
        
        return "{" + ", ".join(items) + "}"
