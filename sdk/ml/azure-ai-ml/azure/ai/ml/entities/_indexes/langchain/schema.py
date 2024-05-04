from dataclasses import dataclass, field

@dataclass
class Document:
    """Class for storing a piece of text and associated metadata."""

    page_content: str
    """String text."""
    metadata: dict = field(default_factory=list)
    """Arbitrary metadata about the page content (e.g., source, relationships to other
        documents, etc.).
    """