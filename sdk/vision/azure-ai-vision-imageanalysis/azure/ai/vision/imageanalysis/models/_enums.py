# coding=utf-8

from enum import Enum
from azure.core import CaseInsensitiveEnumMeta


class VisualFeatures(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """The visual features supported by the Image Analysis service."""

    TAGS = "tags"
    """Extract content tags for thousands of recognizable objects, living beings, scenery, and actions
    that appear in the image."""
    CAPTION = "caption"
    """Generate a human-readable caption sentence that describes the content of the image."""
    DENSE_CAPTIONS = "denseCaptions"
    """Generate human-readable caption sentences for up to 10 different regions in the image,
    including one for the whole image."""
    OBJECTS = "objects"
    """Object detection. This is similar to tags, but focused on detecting physical objects in the
    image and returning their location."""
    READ = "read"
    """Extract printed or handwritten text from the image. Also known as Optical Character Recognition
    (OCR)."""
    SMART_CROPS = "smartCrops"
    """Find representative sub-regions of the image for thumbnail generation, at desired aspect
    ratios, with priority given to detected faces."""
    PEOPLE = "people"
    """Detect people in the image and return their location."""
