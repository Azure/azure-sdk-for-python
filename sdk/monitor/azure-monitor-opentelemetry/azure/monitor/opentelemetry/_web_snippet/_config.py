# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License in the project root for
# license information.
# -------------------------------------------------------------------------

from typing import Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class WebSnippetConfig:
    """Simplified configuration for Web Snippet Injection."""
    
    enabled: bool = False
    connection_string: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary for snippet generation."""
        return {
            "enabled": self.enabled,
            "connectionString": self.connection_string,
            "cfg": {
                "instrumentationKey": self._extract_instrumentation_key(),
                "sdkExtension": "a",  # Python identifier
            }
        }
    
    def _extract_instrumentation_key(self) -> Optional[str]:
        """Extract instrumentation key from connection string."""
        if not self.connection_string:
            return None
            
        parts = self.connection_string.split(";")
        for part in parts:
            if part.strip().lower().startswith("instrumentationkey="):
                return part.split("=", 1)[1].strip()
        return None
