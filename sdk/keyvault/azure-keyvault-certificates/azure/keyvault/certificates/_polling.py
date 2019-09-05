# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import logging
import time

from azure.core.exceptions import HttpResponseError
from azure.core.polling import PollingMethod
from azure.keyvault.certificates._shared import parse_vault_id

logger = logging.getLogger(__name__)


class CreateCertificatePoller(PollingMethod):
    def __init__(self, interval=5, unknown_issuer=False):
        self._command = None
        self._status = None
        self._certificate_id = None
        self.polling_interval = interval
        self.unknown_issuer = unknown_issuer

    def _update_status(self):
        # type: () -> None
        pending_certificate = self._command()
        self._status = pending_certificate.status.lower()
        if not self._certificate_id:
            self._certificate_id = parse_vault_id(pending_certificate.id)

    def initialize(self, client, initial_response, _):
        # type: (Any, Any, Callable) -> None
        self._command = client
        self._status = initial_response

    def run(self):
        # type: () -> None
        try:
            while not self.finished():
                self._update_status()
                if self._status != 'completed' and self._status != 'inprogress' and self._status != 'cancelled':
                    raise HttpResponseError(
                        'Unknown status \'{}\' for pending certificate {}'.format(self._status, self._certificate_id))
                time.sleep(self.polling_interval)
        except Exception as e:
            logger.warning(str(e))
            raise

    def finished(self):
        # type: () -> bool
        if self.unknown_issuer:
            return True
        return self._status != 'inprogress'

    def resource(self):
        # type: () -> str
        if not self.finished():
            self._update_status()
        return self._status

    def status(self):
        # type: () ->str
        return self._status
