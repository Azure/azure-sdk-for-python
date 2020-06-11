"""Provides auxiliary functionality to the `msal` package."""
__version__ = "0.1.3"

import sys

if sys.platform.startswith('win'):
    from .token_cache import WindowsTokenCache as TokenCache
elif sys.platform.startswith('darwin'):
    from .token_cache import OSXTokenCache as TokenCache
else:
    from .token_cache import UnencryptedTokenCache as TokenCache
