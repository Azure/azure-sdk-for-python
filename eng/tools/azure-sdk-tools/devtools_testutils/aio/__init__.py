from .proxy_testcase_async import recorded_by_proxy_async

# Import httpx decorator if httpx is available
try:
    from .proxy_testcase_async_httpx import recorded_by_proxy_async_httpx
    _httpx_available = True
except ImportError:
    _httpx_available = False

__all__ = ["recorded_by_proxy_async"]

# Add httpx decorator if available
if _httpx_available:
    __all__.append("recorded_by_proxy_async_httpx")
