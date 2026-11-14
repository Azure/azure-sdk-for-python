# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Refresh in-process random generators after a memory snapshot restore.

A memory snapshot copies the whole process, so every sandbox restored from the
same snapshot starts with identical in-process generator state. Python's
``random`` module (which also produces OpenTelemetry trace and span IDs),
NumPy's legacy global generator, and OpenSSL's generators would otherwise
return the same sequence in every restored sandbox.

These helpers draw fresh bytes from the operating system. They never import a
library or module that the application has not already loaded, and never raise.
"""

import logging
import os
import random
import struct
import sys

logger = logging.getLogger("azure.ai.agentserver")

_ENTROPY_BYTES = 32
_CRYPTOGRAPHY_RUST_MODULE = "cryptography.hazmat.bindings._rust"
_NUMPY_RANDOM_MODULE = "numpy.random"


def add_openssl_entropy() -> list[str]:
    """Add operating-system entropy to the OpenSSL generators loaded in this process.

    Covers the OpenSSL instance used by the ``ssl`` module and, when the
    ``cryptography`` native module is already loaded, the separate OpenSSL
    instance that ``cryptography`` wheels bundle, reached through that loaded
    module. Adding entropy is always safe, so this can run on every
    after-restore call.

    :return: Names of the generators that received entropy.
    :rtype: list[str]
    """
    refreshed: list[str] = []
    try:
        import ssl  # pylint: disable=import-outside-toplevel

        ssl.RAND_add(os.urandom(_ENTROPY_BYTES), float(_ENTROPY_BYTES))
        refreshed.append("ssl")
    except Exception as exc:  # pylint: disable=broad-exception-caught
        logger.warning("Could not add entropy to the ssl module's OpenSSL generator: %s", type(exc).__name__)

    rust_module = sys.modules.get(_CRYPTOGRAPHY_RUST_MODULE)
    if rust_module is not None:
        try:
            openssl_lib = getattr(getattr(rust_module, "_openssl", None), "lib", None)
            rand_add = getattr(openssl_lib, "RAND_add", None)
            if rand_add is None:
                logger.warning("Could not add entropy to the cryptography OpenSSL generator: RAND_add is unavailable")
            else:
                rand_add(os.urandom(_ENTROPY_BYTES), _ENTROPY_BYTES, float(_ENTROPY_BYTES))
                refreshed.append("cryptography")
        except Exception as exc:  # pylint: disable=broad-exception-caught
            logger.warning("Could not add entropy to the cryptography OpenSSL generator: %s", type(exc).__name__)
    return refreshed


def reseed_python_generators() -> list[str]:
    """Reseed Python's global ``random`` generator and NumPy's legacy global generator.

    NumPy is reseeded only when ``numpy.random`` is already loaded; if it is
    loaded later, it seeds itself from the operating system at that point.

    :return: Names of the generators that were reseeded.
    :rtype: list[str]
    """
    refreshed: list[str] = []
    try:
        random.seed(os.urandom(_ENTROPY_BYTES))
        refreshed.append("random")
    except Exception as exc:  # pylint: disable=broad-exception-caught
        logger.warning("Could not reseed the random module: %s", type(exc).__name__)

    numpy_random = sys.modules.get(_NUMPY_RANDOM_MODULE)
    if numpy_random is not None:
        try:
            numpy_random.seed(list(struct.unpack("<8I", os.urandom(_ENTROPY_BYTES))))
            refreshed.append("numpy.random")
        except Exception as exc:  # pylint: disable=broad-exception-caught
            logger.warning("Could not reseed numpy.random: %s", type(exc).__name__)
    return refreshed
