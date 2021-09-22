# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import logging
import time

from azure.core.polling import PollingMethod

try:
    from typing import TYPE_CHECKING
except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
    # pylint: disable=ungrouped-imports
    from typing import Any, Callable, Union
    from azure.keyvault.certificates import KeyVaultCertificate, CertificateOperation

logger = logging.getLogger(__name__)


class CreateCertificatePoller(PollingMethod):
    def __init__(self, get_certificate_command, interval=5):
        self._command = None
        self._resource = None
        self._pending_certificate_op = None
        self._get_certificate_command = get_certificate_command
        self._polling_interval = interval

    def _update_status(self):
        # type: () -> None
        self._pending_certificate_op = self._command()

    def initialize(self, client, initial_response, _):
        # type: (Any, Any, Callable) -> None
        self._command = client
        self._pending_certificate_op = initial_response

    def run(self):
        # type: () -> None
        try:
            while not self.finished():
                self._update_status()
                if not self.finished():
                    time.sleep(self._polling_interval)
            if self._pending_certificate_op.status.lower() == "completed":
                self._resource = self._get_certificate_command()
            else:
                self._resource = self._pending_certificate_op
        except Exception as e:
            logger.warning(str(e))
            raise

    def finished(self):
        # type: () -> bool
        if self._pending_certificate_op.issuer_name.lower() == "unknown":
            return True
        return self._pending_certificate_op.status.lower() != "inprogress"

    def resource(self):
        # type: () -> Union[KeyVaultCertificate, CertificateOperation]
        return self._resource

    def status(self):
        # type: () -> str
        return self._pending_certificate_op.status.lower()
