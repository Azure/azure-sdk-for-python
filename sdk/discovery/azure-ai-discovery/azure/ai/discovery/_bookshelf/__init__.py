# Re-export BookshelfClient from the generated sub-client
from .azure.ai.discovery import BookshelfClient  # type: ignore

__all__ = ["BookshelfClient"]
