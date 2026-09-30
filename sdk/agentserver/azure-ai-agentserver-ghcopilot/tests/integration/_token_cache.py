"""Shared Azure token cache for integration test scripts.

Caches the access token to a temp file (~50min TTL) to avoid repeated
`az account get-access-token` calls (~5s each).
"""

import json
import os
import subprocess
import sys
import time
from pathlib import Path

_CACHE_FILE = Path(os.environ.get("TEMP", "/tmp")) / "foundry_token_cache.json"
_TTL_SECONDS = 50 * 60  # 50 minutes (tokens last ~1hr)


def get_access_token(resource: str = "https://ai.azure.com") -> str:
    """Get an Azure access token, using cache if available."""
    # Check cache
    if _CACHE_FILE.exists():
        try:
            age = time.time() - _CACHE_FILE.stat().st_mtime
            if age < _TTL_SECONDS:
                cache = json.loads(_CACHE_FILE.read_text())
                if cache.get("resource") == resource and cache.get("token"):
                    return cache["token"]
        except Exception:
            pass

    # Cache miss — fetch new token
    print("[token] Fetching new token...", file=sys.stderr)
    cmd = ["az", "account", "get-access-token", "--resource", resource, "-o", "json"]
    result = subprocess.run(
        cmd, capture_output=True, encoding="utf-8", errors="replace",
        shell=(sys.platform == "win32"),
    )
    if result.returncode != 0:
        print("Failed to get access token. Run 'az login' first.", file=sys.stderr)
        sys.exit(1)

    raw = json.loads(result.stdout)
    token = raw["accessToken"]

    # Save cache
    try:
        _CACHE_FILE.write_text(json.dumps({"token": token, "resource": resource}))
    except Exception:
        pass

    return token
