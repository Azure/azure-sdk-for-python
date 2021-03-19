# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------


class ContainerRegistryTokenCredential(object):
    """Token credential representing the container registry refresh token.
        This token is unique per registry operation,

    :param token_service: TokenServiceImplementation
    :type token_service: TokenServiceImpl
    :param token_credential: AAD Token Credential
    :type token_credential: :class:`~azure.core.credential.TokenCredential`
    """

    AAD_DEFAULT_SCOPE = "https://management.core.windows.net/.default"

    def __init__(self, token_service, aad_token_credential):
        # type: (TokenServiceImpl, TokenCredential) -> None
        self.token_service = token_service
        self.token_credential = aad_token_credential

    def get_token(self, context):
        # type: (ContainerRegistryTokenRequestContext) -> AccessToken
        service_name = context.get_service_name()

        token = self.token_credential.get_token(
            TokenRequestContext().add_scopes(self.AAD_DEFAULT_SCOPE)
        )

        return self.token_service.get_acr_refresh_token(token.get_token, service_name)
