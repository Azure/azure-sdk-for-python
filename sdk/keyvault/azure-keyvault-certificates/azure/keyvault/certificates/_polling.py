# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import logging
import time
from typing import Any, Callable, Optional, Union

from azure.core.polling import PollingMethod
from azure.keyvault.certificates import KeyVaultCertificate, CertificateOperation


logger = logging.getLogger(__name__)


class CreateCertificatePoller(PollingMethod):
    def __init__(self, get_certificate_command: Callable, interval: int = 5) -> None:
        self._command: Optional[Callable] = None
        self._resource: Optional[Union[CertificateOperation, KeyVaultCertificate]] = None
        self._pending_certificate_op: Optional[CertificateOperation] = None
        self._get_certificate_command = get_certificate_command
        self._polling_interval = interval

    def _update_status(self) -> None:
        self._pending_certificate_op = self._command() if self._command else None

    def initialize(self, client: Any, initial_response: Any, _: Callable) -> None:
        self._command = client
        self._pending_certificate_op = initial_response

    def run(self) -> None:
        try:
            while not self.finished():
                self._update_status()
                if not self.finished():
                    time.sleep(self._polling_interval)
            operation = self._pending_certificate_op
            if operation and operation.status and operation.status.lower() == "completed":
                self._resource = self._get_certificate_command()
            else:
                self._resource = self._pending_certificate_op
        except Exception as e:
            logger.warning(str(e))
            raise

    def finished(self) -> bool:
        operation = self._pending_certificate_op
        if operation and operation.issuer_name and operation.issuer_name.lower() == "unknown":
            return True
        return self._pending_certificate_op.status.lower() != "inprogress"  # type: ignore

    def resource(self) -> Union[KeyVaultCertificate, CertificateOperation]:
        return self._resource  # type: ignore

    def status(self) -> str:
        return self._pending_certificate_op.status.lower()  # type: ignore
