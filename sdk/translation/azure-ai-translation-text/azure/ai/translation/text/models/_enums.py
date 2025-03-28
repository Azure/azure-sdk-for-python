# coding=utf-8

from enum import Enum
from azure.core import CaseInsensitiveEnumMeta


class LanguageDirectionality(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Language Directionality."""

    LEFT_TO_RIGHT = "ltr"
    """Language is written left to right."""
    RIGHT_TO_LEFT = "rtl"
    """Language is written right to left."""


class ProfanityAction(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Translator profanity actions."""

    NO_ACTION = "NoAction"
    """No Action is taken on profanity"""
    MARKED = "Marked"
    """Profanity is marked."""
    DELETED = "Deleted"
    """Profanity is deleted from the translated text."""


class ProfanityMarker(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Translator profanity markers."""

    ASTERISK = "Asterisk"
    """Profanity is marked with asterisk."""
    TAG = "Tag"
    """Profanity is marked with the tags."""


class TextType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Translation text type."""

    PLAIN = "Plain"
    """Plain text."""
    HTML = "Html"
    """HTML-encoded text."""
