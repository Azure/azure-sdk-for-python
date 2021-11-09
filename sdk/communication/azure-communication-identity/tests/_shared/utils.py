# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------

from azure.core.pipeline.policies import HttpLoggingPolicy
from msal import PublicClientApplication

def get_http_logging_policy(**kwargs):
    http_logging_policy = HttpLoggingPolicy(**kwargs)
    http_logging_policy.allowed_header_names.update(
        {
            "MS-CV"
        }
    )
    return http_logging_policy

def generate_teams_user_aad_token(
            m365_app_id, # type: str
            m365_aad_authority, # type: str
            m365_aad_tenant, # type: str
            msal_username, # type: str
            msal_password, # type: str
            m365_scope # type: str
):
    # type: (...) -> str
    """Returns issued AAD access token of a Teams User by MSAL library
    :param m365_app_id: the application id of M365
    :type m365_app_id: str
    :param m365_aad_authority: the AAD authority of M365
    :type m365_aad_authority: str
    :param m365_aad_tenant: the tenant ID of M365 application
    :type m365_aad_tenant: str
    :param msal_username: the username for authenticating via MSAL library
    :type msal_username: str
    :param msal_password: the password for authenticating via MSAL library
    :type msal_password: str
    :param m365_scope: the scope of M365 application
    :type m365_scope: str
    :return: an AAD access token of a Teams User
    :rtype: str
    """
    msal_app = PublicClientApplication(
        client_id=m365_app_id,
        authority="{}/{}".format(m365_aad_authority, m365_aad_tenant))
    result = msal_app.acquire_token_by_username_password(
        username=msal_username,
        password=msal_password,
        scopes=[m365_scope])
    return result["access_token"]
