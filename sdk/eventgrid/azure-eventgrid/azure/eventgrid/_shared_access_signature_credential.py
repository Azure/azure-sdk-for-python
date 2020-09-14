# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------

class EventGridSharedAccessSignatureCredential(object):
    """Creates an instance of an EventGridSharedAccessSignatureCredential for use with a service client.
       :param str signature: Signature to use in authentication.
    """

    def __init__(self, signature):
        # type: (str) -> None
        self._signature = signature

    @property
    def signature(self):
        # type: () -> str
        """
        The value of the signature to be used in authentication.

        :rtype: str
        """
        return self._signature

    def update(self, signature):
        # type: (str) -> None
        """
        Updates the key property value of the signature to be used in authentication.

        :param str signature: Signature to use in authentication.
        """
        self._signature = signature
