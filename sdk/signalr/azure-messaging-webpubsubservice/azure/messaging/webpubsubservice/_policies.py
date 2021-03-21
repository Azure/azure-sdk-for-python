import datetime
import typing
import jwt

if typing.TYPE_CHECKING:
    from azure.core.credentials import AzureKeyCredential
    from azure.core.pipeline import PipelineRequest

from azure.core.pipeline.policies import SansIOHTTPPolicy


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
        return super(JwtCredentialPolicy, self).on_request(request)

    def _encode(self, url):
        # type: (AzureKeyCredential) -> str
        data = {
            "aud": url,
            "exp": datetime.datetime.now(tz=datetime.timezone.utc)
            + datetime.timedelta(seconds=60),
        }
        if self._user:
            data[self.NAME_CLAIM_TYPE] = self._user

        encoded = jwt.encode(
            payload=data,
            key=self._credential.key,
            algorithm="HS256",
        )
        return typing.cast(str, encoded)  # jwt's typing is incorrect...
