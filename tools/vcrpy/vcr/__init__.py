import logging
import warnings
import sys
from .config import VCR

# Set default logging handler to avoid "No handler found" warnings.
try:  # Python 2.7+
    from logging import NullHandler
except ImportError:

    class NullHandler(logging.Handler):
        def emit(self, record):
            pass


if sys.version_info[0] == 2:
    warnings.warn(
        "Python 2.x support of vcrpy is deprecated and will be removed in an upcoming major release.",
        DeprecationWarning,
    )

logging.getLogger(__name__).addHandler(NullHandler())


default_vcr = VCR()
use_cassette = default_vcr.use_cassette
