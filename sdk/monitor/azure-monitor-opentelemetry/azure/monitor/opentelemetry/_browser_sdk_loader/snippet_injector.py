# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License in the project root for
# license information.
# -------------------------------------------------------------------------

import gzip
import importlib
import re
from logging import getLogger
from typing import Any, Dict, Optional, Tuple

from ._config import BrowserSDKConfig

# Optional compression libraries
_BROTLI_MODULE: Optional[Any]
try:
    _BROTLI_MODULE = importlib.import_module("brotli")
    HAS_BROTLI = True
except ImportError:
    _BROTLI_MODULE = None
    HAS_BROTLI = False

_ZLIB_MODULE: Optional[Any]
try:
    import zlib as _imported_zlib

    _ZLIB_MODULE = _imported_zlib
    HAS_ZLIB = True
except ImportError:
    _ZLIB_MODULE = None
    HAS_ZLIB = False

_logger = getLogger(__name__)


def _mark_browser_loader_feature(is_enabled: bool) -> None:
    """Record browser SDK loader usage in statsbeat when available.

    :param is_enabled: Indicates whether the browser loader is enabled.
    :type is_enabled: bool
    """
    if not is_enabled:
        return
    try:
        from azure.monitor.opentelemetry.exporter.statsbeat._state import (
            get_statsbeat_browser_sdk_loader_feature_set,
            get_statsbeat_shutdown,
            is_statsbeat_enabled,
            set_statsbeat_browser_sdk_loader_feature_set,
        )
    except ImportError:
        return

    try:
        if (
            is_statsbeat_enabled()
            and not get_statsbeat_shutdown()
            and not get_statsbeat_browser_sdk_loader_feature_set()
        ):
            set_statsbeat_browser_sdk_loader_feature_set()
    except Exception:  # pylint: disable=broad-exception-caught
        _logger.debug("Failed to record browser loader statsbeat usage", exc_info=True)


# Web SDK snippet template
_WEB_SDK_SNIPPET_TEMPLATE = """<script type="text/javascript">
!function(T,l,y){var S=T.location,k="script",D="instrumentationKey",C="ingestionendpoint",I="disableExceptionTracking",E="ai.device.",b="toLowerCase",w="crossOrigin",N="POST",e="appInsightsSDK",t=y.name||"appInsights";(y.name||T[e])&&(T[e]=t);var n=T[t]||function(d){var g=!1,f=!1,m={initialize:!0,queue:[],sv:"5",version:2,config:d};function v(e,t){var n={},a="Browser";return n[E+"id"]=a[b](),n[E+"type"]=a,n["ai.operation.name"]=S&&S.pathname||"_unknown_",n["ai.internal.sdkVersion"]="javascript:snippet_"+(m.sv||m.version),{time:function(){var a=new Date;function b(e){var t=""+e;return 1===t.length&&(t="0"+t),t}return a.getUTCFullYear()+"-"+b(1+a.getUTCMonth())+"-"+b(a.getUTCDate())+"T"+b(a.getUTCHours())+":"+b(a.getUTCMinutes())+":"+b(a.getUTCSeconds())+"."+((a.getUTCMilliseconds()/1e3).toFixed(3)+"").slice(2,5)+"Z"}(),iKey:e,name:"Microsoft.ApplicationInsights."+t.replace(/\\s/g,"")+"."+v,sampleRate:100,tags:n,data:{baseData:{ver:2}}}}var h=d.url||y.src;if(h){function a(e){var t,n,a,i,r,o,s,c,u,p,l;g=!0,m.queue=[],f||(f=!0,t=h,s=function(){var e={},t=d.connectionString;if(t)for(var n=t.split(";"),a=0;a<n.length;a++){var i=n[a].split("=");2===i.length&&(e[i[0][b]()]=i[1])}if(!e[C]){var r=e.endpointsuffix,o=r?e.location:null;e[C]="https://"+(o?o+".":"")+"dc."+(r||"services.visualstudio.com")}return e}(),c=s[D]||d[D]||"",u=s[C],p=u?u+"/v2/track":d.endpointUrl,(l=[]).push((n="SDK LOAD Failure: Failed to load Application Insights SDK script (See stack for details)",a=t,i=p,(o=(r=v(c,"Exception")).data).baseType="ExceptionData",o.baseData.exceptions=[{typeName:"SDKLoadFailed",message:n.replace(/\\./g,"-"),hasFullStack:!1,stack:n+"\\nSnippet failed to load ["+a+"] -- Telemetry is disabled\\nHelp Link: https://go.microsoft.com/fwlink/?linkid=2128109\\nHost: "+(S&&S.pathname||"_unknown_")+"\\nEndpoint: "+i,parsedStack:[]}],r)),l.push(function(e,t,n,a){var i=v(c,"Message"),r=i.data;r.baseType="MessageData";var o=r.baseData;return o.message='AI (Internal): 99 message:"'+("SDK LOAD Failure: Failed to load Application Insights SDK script (See stack for details) ("+n+")").replace(/\\"/g,"")+'"',o.properties={endpoint:a},i}(0,0,t,p)),function(e,t){if(JSON){var n=T.fetch;if(n&&!y.useXhr)n(t,{method:N,body:JSON.stringify(e),mode:"cors"});else if(XMLHttpRequest){var a=new XMLHttpRequest;a.open(N,t),a.setRequestHeader("Content-type","application/json"),a.send(JSON.stringify(e))}}}(l,p))}function i(e,t){f||setTimeout(function(){!t&&m.core||a()},500)}var e=function(){var n=l.createElement(k);n.src=h;var e=y[w];return!e&&""!==e||"undefined"==n[w]||(n[w]=e),n.onload=i,n.onerror=a,n.onreadystatechange=function(e,t){"loaded"!==n.readyState&&"complete"!==n.readyState||i(0,t)},n}();y.ld<0?l.getElementsByTagName("head")[0].appendChild(e):setTimeout(function(){l.getElementsByTagName(k)[0].parentNode.insertBefore(e,l.getElementsByTagName(k)[0])},y.ld||0)}try{m.cookie=l.cookie}catch(p){}function t(e){for(;e.length;)!function(t){m[t]=function(){var e=arguments;g||m.queue.push(function(){m[t].apply(m,e)})}}(e.pop())}var n="track",r="TrackPage",o="TrackEvent";t([n+"Event",n+"PageView",n+"Exception",n+"Trace",n+"DependencyData",n+"Metric",n+"PageViewPerformance","start"+r,"stop"+r,"start"+o,"stop"+o,"addTelemetryInitializer","setAuthenticatedUserContext","clearAuthenticatedUserContext","flush"]),m.SeverityLevel={Verbose:0,Information:1,Warning:2,Error:3,Critical:4};var s=(d.extensionConfig||{}).ApplicationInsightsAnalytics||{};if(!0!==d[I]&&!0!==s[I]){var c="onerror";t(["_"+c]);var u=T[c];T[c]=function(e,t,n,a,i){var r=u&&u(e,t,n,a,i);return!0!==r&&m["_"+c]({message:e,url:t,lineNumber:n,columnNumber:a,error:i}),r},d.autoExceptionInstrumented=!0}return m}(y.cfg);function a(){y.onInit&&y.onInit(n)}(T[t]=n).queue&&0===n.queue.length?(n.queue.push(a),n.trackPageView({})):a()}(window,document,{
src: "https://js.monitor.azure.com/scripts/b/ai.2.min.js",
cfg: {CONFIG_PLACEHOLDER}
});
</script>"""


class WebSnippetInjector:
    """Handles injection of Application Insights web snippet into HTML responses.

    :param config: Configuration object for the web snippet injector.
    :type config: BrowserSDKConfig
    """

    def __init__(self, config: BrowserSDKConfig) -> None:
        """Initialize the WebSnippetInjector.

        :param config: Configuration object for the web snippet injector.
        :type config: BrowserSDKConfig
        :rtype: None
        """
        self.config = config
        self._web_sdk_snippet_cache: Optional[str] = None
        self._decompressed_content_cache: Optional[bytes] = None
        self._cache_key: Optional[tuple] = None
        # Regex patterns for detecting existing Web SDK - more specific to avoid false positives
        self._existing_sdk_patterns = [
            # Look for actual JavaScript variables/objects, not just text content
            re.compile(r"\bappInsights\s*[=\.]", re.IGNORECASE),  # appInsights= or appInsights.
            re.compile(r"\bApplicationInsights\s*[=\.]", re.IGNORECASE),  # ApplicationInsights= or ApplicationInsights.
            re.compile(r"window\[.*appInsights.*\]", re.IGNORECASE),  # window["appInsights"] patterns
            re.compile(r"Microsoft\.ApplicationInsights", re.IGNORECASE),  # Microsoft.ApplicationInsights namespace
            # Look for actual script URLs
            re.compile(r"ai\.2\.min\.js", re.IGNORECASE),
            re.compile(r"js\.monitor\.azure\.com", re.IGNORECASE),
            # Look for HTML comments indicating snippet is already present
            re.compile(
                r"<!--.*(appinsights|application\s+insights).*snippet.*(already|here|present).*-->", re.IGNORECASE
            ),
        ]
        _mark_browser_loader_feature(self.config.enabled)

    def should_inject(
        self, request_method: str, content_type: Optional[str], content: bytes, content_encoding: Optional[str] = None
    ) -> bool:
        """Determine whether the web snippet should be injected into the response.

        :param request_method: HTTP request method (e.g., 'GET', 'POST').
        :type request_method: str
        :param content_type: Content-Type header value from the response.
        :type content_type: str or None
        :param content: Response content bytes.
        :type content: bytes
        :param content_encoding: Content-Encoding header value (e.g., 'gzip', 'br').
        :type content_encoding: str or None
        :return: True if the snippet should be injected, False otherwise.
        :rtype: bool
        """
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
        """Inject the web snippet into HTML content.

        :param content: HTML content as bytes to inject the snippet into.
        :type content: bytes
        :param encoding: Text encoding to use for decoding/encoding content.
        :type encoding: str
        :return: Modified HTML content with the injected snippet.
        :rtype: bytes
        """
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
            modified_html = html_content[:insertion_point] + snippet + html_content[insertion_point:]
            return modified_html.encode(encoding)
        except Exception as ex:  # pylint: disable=broad-exception-caught
            _logger.warning("Failed to inject web snippet: %s", ex, exc_info=True)
            return content

    def inject_with_compression(
        self, content: bytes, content_encoding: Optional[str] = None, encoding: str = "utf-8"
    ) -> Tuple[bytes, Optional[str]]:  # pylint: disable=too-many-return-statements
        """Inject snippet handling compression/decompression efficiently using cached decompressed content.

        :param content: Response content bytes, potentially compressed.
        :type content: bytes
        :param content_encoding: Content-Encoding header value (e.g., 'gzip', 'br', 'deflate').
        :type content_encoding: str or None
        :param encoding: Text encoding to use for decoding/encoding HTML content.
        :type encoding: str
        :return: Tuple of (modified_content, detected_encoding) where modified_content is the
         response content with injected snippet and detected_encoding is the compression format used.
        :rtype: Tuple[bytes, Optional[str]]
        """
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
                    except Exception:  # pylint: disable=broad-exception-caught
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
            return modified_content, None
        except Exception as ex:  # pylint: disable=broad-exception-caught
            _logger.warning("Failed to inject snippet with compression handling: %s", ex, exc_info=True)
            return content, content_encoding

    def _get_web_snippet(self) -> str:
        """Generate the web snippet with configuration.

        :return: The complete web snippet JavaScript code as a string.
        :rtype: str
        """
        if self._web_sdk_snippet_cache is None:
            config_dict = self.config.to_dict()
            config_json = self._dict_to_js_object(config_dict.get("cfg", {}))
            self._web_sdk_snippet_cache = _WEB_SDK_SNIPPET_TEMPLATE.replace("{CONFIG_PLACEHOLDER}", config_json)
        return self._web_sdk_snippet_cache

    def _get_decompressed_content(self, content: bytes, content_encoding: Optional[str] = None) -> bytes:
        """Get decompressed content with caching to avoid redundant decompression.

        :param content: Content bytes to decompress if needed.
        :type content: bytes
        :param content_encoding: Content-Encoding header value (e.g., 'gzip', 'br', 'deflate').
        :type content_encoding: str or None
        :return: Decompressed content bytes.
        :rtype: bytes
        """
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
                except Exception:  # pylint: disable=broad-exception-caught
                    continue
        # Cache the result only if we actually did decompression work
        if content_encoding or decompressed_content != content:
            self._cache_key = cache_key
            self._decompressed_content_cache = decompressed_content
        return decompressed_content

    def _appears_compressed(self, content: bytes) -> bool:
        """Quick check if content appears to be compressed based on magic numbers.

        :param content: Content bytes to check for compression signatures.
        :type content: bytes
        :return: True if content appears to be compressed, False otherwise.
        :rtype: bool
        """
        if len(content) < 3:
            return False
        # Check for common compression magic numbers
        # Gzip: starts with 0x1f 0x8b
        if content.startswith(b"\x1f\x8b"):
            return True
        # Brotli: no reliable magic number, but check for common patterns
        # (Brotli detection is harder without trying to decompress)
        # zlib/deflate: starts with 0x78 followed by various values
        if content[0] == 0x78 and content[1] in (0x01, 0x5E, 0x9C, 0xDA):
            return True
        return False

    def _clear_decompression_cache(self) -> None:
        """Clear the decompressed content cache.

        :rtype: None
        """
        self._decompressed_content_cache = None
        self._cache_key = None

    def _has_existing_web_sdk(self, content: bytes, content_encoding: Optional[str] = None) -> bool:
        """Check if Web SDK is already present in the HTML, handling compressed content.

        :param content: HTML content bytes to check for existing Web SDK.
        :type content: bytes
        :param content_encoding: Content-Encoding header value (e.g., 'gzip', 'br', 'deflate').
        :type content_encoding: str or None
        :return: True if Web SDK is detected in the content, False otherwise.
        :rtype: bool
        """
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
                    except Exception:  # pylint: disable=broad-exception-caught
                        continue
            return self._has_existing_web_sdk_from_decompressed(decompressed_content)

        except Exception:  # pylint: disable=broad-exception-caught
            return False

    def _has_existing_web_sdk_from_decompressed(self, decompressed_content: bytes) -> bool:
        """Check if Web SDK is already present in decompressed HTML content.

        :param decompressed_content: Decompressed HTML content bytes to scan for Web SDK patterns.
        :type decompressed_content: bytes
        :return: True if Web SDK patterns are found, False otherwise.
        :rtype: bool
        """
        try:
            # Convert decompressed content to string and check for patterns
            content_str = decompressed_content.decode("utf-8", errors="ignore")
            return any(pattern.search(content_str) for pattern in self._existing_sdk_patterns)
        except Exception:  # pylint: disable=broad-exception-caught
            return False

    def _find_insertion_point(self, html_content: str) -> int:
        """Find the best insertion point for the snippet.

        :param html_content: HTML content as a string to search for insertion points.
        :type html_content: str
        :return: Character position where snippet should be inserted, or -1 if no suitable point found.
        :rtype: int
        """
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
        """Decompress content based on encoding.

        :param content: Compressed content bytes to decompress.
        :type content: bytes
        :param encoding: Compression encoding type (e.g., 'gzip', 'br', 'deflate').
        :type encoding: str or None
        :return: Decompressed content bytes.
        :rtype: bytes
        """
        if not encoding:
            return content

        result = content
        try:
            normalized = encoding.lower()
            if normalized == "gzip":
                result = gzip.decompress(content)
            elif normalized == "br":
                if not HAS_BROTLI or _BROTLI_MODULE is None:
                    _logger.warning("brotli library not available for decompression")
                else:
                    result = _BROTLI_MODULE.decompress(content)
            elif normalized == "deflate":
                if not HAS_ZLIB or _ZLIB_MODULE is None:
                    _logger.warning("zlib library not available for decompression")
                else:
                    result = _ZLIB_MODULE.decompress(content)
        except Exception as ex:  # pylint: disable=broad-exception-caught
            _logger.warning("Failed to decompress content with encoding %s: %s", encoding, ex)
        return result

    def _compress_content(self, content: bytes, encoding: str) -> bytes:
        """Compress content using specified encoding.

        :param content: Uncompressed content bytes to compress.
        :type content: bytes
        :param encoding: Compression encoding type (e.g., 'gzip', 'br', 'deflate').
        :type encoding: str
        :return: Compressed content bytes.
        :rtype: bytes
        """
        result = content
        try:
            normalized = encoding.lower()
            if normalized == "gzip":
                result = gzip.compress(content)
            elif normalized == "br":
                if not HAS_BROTLI or _BROTLI_MODULE is None:
                    _logger.warning("brotli library not available for compression")
                else:
                    result = _BROTLI_MODULE.compress(content)
            elif normalized == "deflate":
                if not HAS_ZLIB or _ZLIB_MODULE is None:
                    _logger.warning("zlib library not available for compression")
                else:
                    result = _ZLIB_MODULE.compress(content)
        except Exception as ex:  # pylint: disable=broad-exception-caught
            _logger.warning("Failed to compress content with encoding %s: %s", encoding, ex)
        return result

    def _format_config_value(self, value):
        """Format a configuration value for JavaScript.

        :param value: The value to format.
        :type value: Any
        :return: Formatted string for JavaScript.
        :rtype: str
        """
        if isinstance(value, str):
            return f'"{value}"'
        if isinstance(value, bool):
            return "true" if value else "false"
        if isinstance(value, (int, float)):
            return str(value)
        if isinstance(value, dict):
            return self._dict_to_js_object(value)
        return f'"{str(value)}"'

    def _dict_to_js_object(self, obj: Dict[str, Any]) -> str:
        """Convert Python dict to JavaScript object literal.

        :param obj: Python dictionary to convert to JavaScript object syntax.
        :type obj: Dict[str, Any]
        :return: JavaScript object literal as a string.
        :rtype: str
        """
        items = []
        for key, value in obj.items():
            items.append(f"{key}: {self._format_config_value(value)}")
        return "{" + ", ".join(items) + "}"
