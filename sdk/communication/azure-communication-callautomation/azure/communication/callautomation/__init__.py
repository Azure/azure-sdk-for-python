from ._version import VERSION
from ._call_connection import CallConnection
from ._call_media import CallMedia
from ._call_recording import CallRecording
from ._call_automation_client import CallAutomationClient

__all__ = [
    'CallAutomationClient',
    'CallConnection',
    'CallMedia',
    'CallRecording'
]
__version__ = VERSION
