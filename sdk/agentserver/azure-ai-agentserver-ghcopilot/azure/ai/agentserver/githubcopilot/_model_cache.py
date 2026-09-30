"""Model discovery cache to avoid repeated discovery calls.

Caches discovered models and the selected model per resource URL.
Cache expires after 24 hours or can be manually invalidated.
"""

import json
import logging
import time
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class ModelCache:
    """Cache for discovered models and selected model."""

    def __init__(self, cache_dir: Optional[Path] = None):
        """Initialize model cache.

        Args:
            cache_dir: Directory for cache file (defaults to ~/.foundry-agent)
        """
        if cache_dir is None:
            cache_dir = Path.home() / ".foundry-agent"

        self.cache_dir = cache_dir
        self.cache_file = cache_dir / "model_cache.json"
        self._cache: Dict = {}
        self._load_cache()

    def _load_cache(self):
        """Load cache from disk."""
        try:
            if self.cache_file.exists():
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    self._cache = json.load(f)
                logger.debug("Loaded model cache from disk")
        except Exception as e:
            logger.warning(f"Failed to load model cache: {e}")
            self._cache = {}

    def _save_cache(self):
        """Save cache to disk."""
        try:
            # Ensure cache directory exists
            self.cache_dir.mkdir(parents=True, exist_ok=True)

            # Save cache
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self._cache, f, indent=2)

            # Set restrictive permissions
            self.cache_file.chmod(0o600)

            logger.debug("Saved model cache to disk")
        except Exception as e:
            logger.warning(f"Failed to save model cache: {e}")

    def _get_cache_key(self, resource_url: str) -> str:
        """Get cache key for a resource URL.

        Args:
            resource_url: Azure resource URL

        Returns:
            Cache key (normalized URL)
        """
        return resource_url.lower().rstrip('/')

    def get_selected_model(self, resource_url: str, max_age_seconds: int = 86400) -> Optional[str]:
        """Get cached selected model for a resource.

        Args:
            resource_url: Azure resource URL
            max_age_seconds: Maximum cache age in seconds (default: 24 hours)

        Returns:
            Cached model name or None if not cached/expired
        """
        cache_key = self._get_cache_key(resource_url)

        if cache_key not in self._cache:
            return None

        entry = self._cache[cache_key]
        cached_time = entry.get("timestamp", 0)
        current_time = time.time()

        # Check if cache is expired
        if current_time - cached_time > max_age_seconds:
            age_hours = int((current_time - cached_time) / 3600)
            logger.info(f"Model cache expired for {resource_url} (age: {age_hours}h)")
            return None

        selected_model = entry.get("selected_model")
        if selected_model:
            age_hours = (current_time - cached_time) / 3600
            logger.info(f"Using cached model: {selected_model} (cached {age_hours:.1f} hours ago)")

        return selected_model

    def set_selected_model(
        self,
        resource_url: str,
        model_name: str,
        deployments: Optional[List[Dict]] = None
    ):
        """Cache the selected model for a resource.

        Args:
            resource_url: Azure resource URL
            model_name: Selected model deployment name
            deployments: Optional list of all discovered deployments
        """
        cache_key = self._get_cache_key(resource_url)

        # Prepare cache entry
        entry = {
            "timestamp": time.time(),
            "selected_model": model_name,
        }

        # Optionally cache the full deployment list
        if deployments:
            entry["deployments"] = deployments

        self._cache[cache_key] = entry
        self._save_cache()

        logger.info(f"Cached selected model: {model_name} for {resource_url}")

    def invalidate(self, resource_url: Optional[str] = None):
        """Invalidate cache for a specific resource or all resources.

        Args:
            resource_url: Resource URL to invalidate (None = invalidate all)
        """
        if resource_url:
            cache_key = self._get_cache_key(resource_url)
            if cache_key in self._cache:
                del self._cache[cache_key]
                self._save_cache()
                logger.info(f"Invalidated cache for {resource_url}")
        else:
            self._cache = {}
            self._save_cache()
            logger.info("Invalidated all model caches")

    def get_cache_info(self, resource_url: str) -> Optional[Dict]:
        """Get cache information for debugging.

        Args:
            resource_url: Azure resource URL

        Returns:
            Cache entry with metadata or None
        """
        cache_key = self._get_cache_key(resource_url)
        entry = self._cache.get(cache_key)

        if entry:
            cached_time = entry.get("timestamp", 0)
            age_hours = (time.time() - cached_time) / 3600
            return {
                "selected_model": entry.get("selected_model"),
                "age_hours": age_hours,
                "cached_at": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(cached_time)),
                "num_deployments": len(entry.get("deployments", [])),
                "deployments": entry.get("deployments", []),  # Include full deployment list
            }

        return None
