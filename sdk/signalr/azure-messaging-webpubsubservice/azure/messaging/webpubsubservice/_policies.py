# --------------------------------------------------------------------------
#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
# The MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the ""Software""), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED *AS IS*, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#
# --------------------------------------------------------------------------

import datetime
import typing
import jwt

from azure.core.pipeline.policies import SansIOHTTPPolicy
if typing.TYPE_CHECKING:
    from azure.core.credentials import AzureKeyCredential
    from azure.core.pipeline import PipelineRequest


class _UTC_TZ(datetime.tzinfo):
    """from https://docs.python.org/2/library/datetime.html#tzinfo-objects"""

    ZERO = datetime.timedelta(0)

    def utcoffset(self, dt):
        return self.__class__.ZERO

    def tzname(self, dt):
        return "UTC"

    def dst(self, dt):
        return self.__class__.ZERO


_UTC = _UTC_TZ()

class JwtCredentialPolicy(SansIOHTTPPolicy):

    NAME_CLAIM_TYPE = "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/name"

    def __init__(self, credential, user=None):
        # type: (AzureKeyCredential, typing.Optional[str]) -> None
        """Create a new instance of the policy associated with the given credential.

        :param credential: The azure.core.credentials.AzureKeyCredential instance to use
        :type credential: ~azure.core.credentials.AzureKeyCredential
        :param user: Optional user name associated with the credential.
        :type user: str
        """
        self._credential = credential
        self._user = user

    def on_request(self, request):
        # type: (PipelineRequest) -> typing.Union[None, typing.Awaitable[None]]
        """Is executed before sending the request from next policy.

        :param request: Request to be modified before sent from next policy.
        :type request: ~azure.core.pipeline.PipelineRequest
        """
        request.http_request.headers["Authorization"] = "Bearer " + self._encode(
            request.http_request.url
        )
        return super(JwtCredentialPolicy, self).on_request(request) # pylint: disable=R1725

    def _encode(self, url):
        # type: (AzureKeyCredential) -> str
        data = {
            "aud": url,
            "exp": datetime.datetime.now(tz=_UTC)
            + datetime.timedelta(seconds=60),
        }
        if self._user:
            data[self.NAME_CLAIM_TYPE] = self._user

        encoded = jwt.encode(
            payload=data,
            key=self._credential.key,
            algorithm="HS256",
        )
        if isinstance(encoded, bytes):
            encoded = encoded.decode('utf8')
        return typing.cast(str, encoded)  # jwt's typing is incorrect...
