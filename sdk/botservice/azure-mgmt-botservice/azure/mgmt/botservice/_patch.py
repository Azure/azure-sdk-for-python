# coding=utf-8
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
from typing import Optional, List
import importlib
import msrest


class WebChatSite(msrest.serialization.Model):
    """A site for the Webchat channel.

    Variables are only populated by the server, and will be ignored when sending a request.

    All required parameters must be populated in order to send to Azure.

    :ivar site_id: Site Id.
    :vartype site_id: str
    :ivar site_name: Required. Site name.
    :vartype site_name: str
    :ivar key: Primary key. Value only returned through POST to the action Channel List API,
     otherwise empty.
    :vartype key: str
    :ivar key2: Secondary key. Value only returned through POST to the action Channel List API,
     otherwise empty.
    :vartype key2: str
    :ivar is_enabled: Required. Whether this site is enabled for DirectLine channel.
    :vartype is_enabled: bool
    :ivar is_webchat_preview_enabled: Required. Whether this site is enabled for preview versions
     of Webchat.
    :vartype is_webchat_preview_enabled: bool
    """

    _validation = {
        'site_id': {'readonly': True},
        'site_name': {'required': True},
        'key': {'readonly': True},
        'key2': {'readonly': True},
        'is_enabled': {'required': True},
        'is_webchat_preview_enabled': {'required': True},
    }

    _attribute_map = {
        'site_id': {'key': 'siteId', 'type': 'str'},
        'site_name': {'key': 'siteName', 'type': 'str'},
        'key': {'key': 'key', 'type': 'str'},
        'key2': {'key': 'key2', 'type': 'str'},
        'is_enabled': {'key': 'isEnabled', 'type': 'bool'},
        'is_webchat_preview_enabled': {'key': 'isWebchatPreviewEnabled', 'type': 'bool'},
    }

    def __init__(
            self,
            *,
            site_name: str,
            is_enabled: bool,
            is_webchat_preview_enabled: bool,
            **kwargs
    ):
        """
        :keyword site_name: Required. Site name.
        :paramtype site_name: str
        :keyword is_enabled: Required. Whether this site is enabled for DirectLine channel.
        :paramtype is_enabled: bool
        :keyword is_webchat_preview_enabled: Required. Whether this site is enabled for preview
         versions of Webchat.
        :paramtype is_webchat_preview_enabled: bool
        """
        super(WebChatSite, self).__init__(
            site_name=site_name,
            is_enabled=is_enabled,
            is_webchat_preview_enabled=is_webchat_preview_enabled,
            **kwargs
        )
        self.site_id = None
        self.site_name = site_name
        self.key = None
        self.key2 = None
        self.is_enabled = is_enabled
        self.is_webchat_preview_enabled = is_webchat_preview_enabled


class DirectLineSite(msrest.serialization.Model):
    """A site for the Direct Line channel.

    Variables are only populated by the server, and will be ignored when sending a request.

    All required parameters must be populated in order to send to Azure.

    :ivar site_id: Site Id.
    :vartype site_id: str
    :ivar site_name: Required. Site name.
    :vartype site_name: str
    :ivar key: Primary key. Value only returned through POST to the action Channel List API,
     otherwise empty.
    :vartype key: str
    :ivar key2: Secondary key. Value only returned through POST to the action Channel List API,
     otherwise empty.
    :vartype key2: str
    :ivar is_enabled: Required. Whether this site is enabled for DirectLine channel.
    :vartype is_enabled: bool
    :ivar is_v1_enabled: Required. Whether this site is enabled for Bot Framework V1 protocol.
    :vartype is_v1_enabled: bool
    :ivar is_v3_enabled: Required. Whether this site is enabled for Bot Framework V1 protocol.
    :vartype is_v3_enabled: bool
    :ivar is_secure_site_enabled: Whether this site is enabled for authentication with Bot
     Framework.
    :vartype is_secure_site_enabled: bool
    :ivar is_block_user_upload_enabled: Whether this site is enabled for block user upload.
    :vartype is_block_user_upload_enabled: bool
    :ivar trusted_origins: List of Trusted Origin URLs for this site. This field is applicable only
     if isSecureSiteEnabled is True.
    :vartype trusted_origins: list[str]
    """

    _validation = {
        'site_id': {'readonly': True},
        'site_name': {'required': True},
        'key': {'readonly': True},
        'key2': {'readonly': True},
        'is_enabled': {'required': True},
        'is_v1_enabled': {'required': True},
        'is_v3_enabled': {'required': True},
    }

    _attribute_map = {
        'site_id': {'key': 'siteId', 'type': 'str'},
        'site_name': {'key': 'siteName', 'type': 'str'},
        'key': {'key': 'key', 'type': 'str'},
        'key2': {'key': 'key2', 'type': 'str'},
        'is_enabled': {'key': 'isEnabled', 'type': 'bool'},
        'is_v1_enabled': {'key': 'isV1Enabled', 'type': 'bool'},
        'is_v3_enabled': {'key': 'isV3Enabled', 'type': 'bool'},
        'is_secure_site_enabled': {'key': 'isSecureSiteEnabled', 'type': 'bool'},
        'is_block_user_upload_enabled': {'key': 'isBlockUserUploadEnabled', 'type': 'bool'},
        'trusted_origins': {'key': 'trustedOrigins', 'type': '[str]'},
    }

    def __init__(
            self,
            *,
            site_name: str,
            is_enabled: bool,
            is_v1_enabled: bool,
            is_v3_enabled: bool,
            is_secure_site_enabled: Optional[bool] = None,
            is_block_user_upload_enabled: Optional[bool] = None,
            trusted_origins: Optional[List[str]] = None,
            **kwargs
    ):
        """
        :keyword site_name: Required. Site name.
        :paramtype site_name: str
        :keyword is_enabled: Required. Whether this site is enabled for DirectLine channel.
        :paramtype is_enabled: bool
        :keyword is_v1_enabled: Required. Whether this site is enabled for Bot Framework V1 protocol.
        :paramtype is_v1_enabled: bool
        :keyword is_v3_enabled: Required. Whether this site is enabled for Bot Framework V1 protocol.
        :paramtype is_v3_enabled: bool
        :keyword is_secure_site_enabled: Whether this site is enabled for authentication with Bot
         Framework.
        :paramtype is_secure_site_enabled: bool
        :keyword is_block_user_upload_enabled: Whether this site is enabled for block user upload.
        :paramtype is_block_user_upload_enabled: bool
        :keyword trusted_origins: List of Trusted Origin URLs for this site. This field is applicable
         only if isSecureSiteEnabled is True.
        :paramtype trusted_origins: list[str]
        """
        super(DirectLineSite, self).__init__(
            site_name=site_name,
            is_enabled=is_enabled,
            is_v1_enabled=is_v1_enabled,
            is_v3_enabled=is_v3_enabled,
            is_secure_site_enabled=is_secure_site_enabled,
            is_block_user_upload_enabled=is_block_user_upload_enabled,
            **kwargs
        )
        self.site_id = None
        self.site_name = site_name
        self.key = None
        self.key2 = None
        self.is_enabled = is_enabled
        self.is_v1_enabled = is_v1_enabled
        self.is_v3_enabled = is_v3_enabled
        self.is_secure_site_enabled = is_secure_site_enabled
        self.is_block_user_upload_enabled = is_block_user_upload_enabled
        self.trusted_origins = trusted_origins


class Site(WebChatSite, DirectLineSite):
    """A site for the channel.

    Variables are only populated by the server, and will be ignored when sending a request.

    All required parameters must be populated in order to send to Azure.

    :ivar is_v1_enabled: Required. Whether this site is enabled for Bot Framework V1 protocol.
    :vartype is_v1_enabled: bool
    :ivar is_v3_enabled: Required. Whether this site is enabled for Bot Framework V1 protocol.
    :vartype is_v3_enabled: bool
    :ivar is_secure_site_enabled: Whether this site is enabled for authentication with Bot
     Framework.
    :vartype is_secure_site_enabled: bool
    :ivar is_block_user_upload_enabled: Whether this site is enabled for block user upload.
    :vartype is_block_user_upload_enabled: bool
    :ivar trusted_origins: List of Trusted Origin URLs for this site. This field is applicable only
     if isSecureSiteEnabled is True.
    :vartype trusted_origins: list[str]
    :ivar site_id: Site Id.
    :vartype site_id: str
    :ivar site_name: Required. Site name.
    :vartype site_name: str
    :ivar key: Primary key. Value only returned through POST to the action Channel List API,
     otherwise empty.
    :vartype key: str
    :ivar key2: Secondary key. Value only returned through POST to the action Channel List API,
     otherwise empty.
    :vartype key2: str
    :ivar is_enabled: Required. Whether this site is enabled for DirectLine channel.
    :vartype is_enabled: bool
    :ivar is_webchat_preview_enabled: Required. Whether this site is enabled for preview versions
     of Webchat.
    :vartype is_webchat_preview_enabled: bool
    :ivar is_token_enabled: Whether this site is token enabled for channel.
    :vartype is_token_enabled: bool
    :ivar e_tag: Entity Tag.
    :vartype e_tag: str
    """

    _validation = {
        'is_v1_enabled': {'required': True},
        'is_v3_enabled': {'required': True},
        'site_id': {'readonly': True},
        'site_name': {'required': True},
        'key': {'readonly': True},
        'key2': {'readonly': True},
        'is_enabled': {'required': True},
        'is_webchat_preview_enabled': {'required': True},
    }

    _attribute_map = {
        'is_v1_enabled': {'key': 'isV1Enabled', 'type': 'bool'},
        'is_v3_enabled': {'key': 'isV3Enabled', 'type': 'bool'},
        'is_secure_site_enabled': {'key': 'isSecureSiteEnabled', 'type': 'bool'},
        'is_block_user_upload_enabled': {'key': 'isBlockUserUploadEnabled', 'type': 'bool'},
        'trusted_origins': {'key': 'trustedOrigins', 'type': '[str]'},
        'site_id': {'key': 'siteId', 'type': 'str'},
        'site_name': {'key': 'siteName', 'type': 'str'},
        'key': {'key': 'key', 'type': 'str'},
        'key2': {'key': 'key2', 'type': 'str'},
        'is_enabled': {'key': 'isEnabled', 'type': 'bool'},
        'is_webchat_preview_enabled': {'key': 'isWebchatPreviewEnabled', 'type': 'bool'},
        'is_token_enabled': {'key': 'isTokenEnabled', 'type': 'bool'},
        'e_tag': {'key': 'eTag', 'type': 'str'},
    }

    def __init__(
            self,
            *,
            is_v1_enabled: bool,
            is_v3_enabled: bool,
            site_name: str,
            is_enabled: bool,
            is_webchat_preview_enabled: bool,
            is_secure_site_enabled: Optional[bool] = None,
            is_block_user_upload_enabled: Optional[bool] = None,
            trusted_origins: Optional[List[str]] = None,
            is_token_enabled: Optional[bool] = None,
            e_tag: Optional[str] = None,
            **kwargs
    ):
        """
        :keyword is_v1_enabled: Required. Whether this site is enabled for Bot Framework V1 protocol.
        :paramtype is_v1_enabled: bool
        :keyword is_v3_enabled: Required. Whether this site is enabled for Bot Framework V1 protocol.
        :paramtype is_v3_enabled: bool
        :keyword is_secure_site_enabled: Whether this site is enabled for authentication with Bot
         Framework.
        :paramtype is_secure_site_enabled: bool
        :keyword is_block_user_upload_enabled: Whether this site is enabled for block user upload.
        :paramtype is_block_user_upload_enabled: bool
        :keyword trusted_origins: List of Trusted Origin URLs for this site. This field is applicable
         only if isSecureSiteEnabled is True.
        :paramtype trusted_origins: list[str]
        :keyword site_name: Required. Site name.
        :paramtype site_name: str
        :keyword is_enabled: Required. Whether this site is enabled for DirectLine channel.
        :paramtype is_enabled: bool
        :keyword is_webchat_preview_enabled: Required. Whether this site is enabled for preview
         versions of Webchat.
        :paramtype is_webchat_preview_enabled: bool
        :keyword is_token_enabled: Whether this site is token enabled for channel.
        :paramtype is_token_enabled: bool
        :keyword e_tag: Entity Tag.
        :paramtype e_tag: str
        """
        super(Site, self).__init__(site_name=site_name, is_enabled=is_enabled,
                                   is_webchat_preview_enabled=is_webchat_preview_enabled, is_v1_enabled=is_v1_enabled,
                                   is_v3_enabled=is_v3_enabled, is_secure_site_enabled=is_secure_site_enabled,
                                   is_block_user_upload_enabled=is_block_user_upload_enabled,
                                   trusted_origins=trusted_origins, **kwargs)
        self.is_v1_enabled = is_v1_enabled
        self.is_v3_enabled = is_v3_enabled
        self.is_secure_site_enabled = is_secure_site_enabled
        self.is_block_user_upload_enabled = is_block_user_upload_enabled
        self.trusted_origins = trusted_origins
        self.is_token_enabled = is_token_enabled
        self.e_tag = e_tag
        self.site_id = None
        self.site_name = site_name
        self.key = None
        self.key2 = None
        self.is_enabled = is_enabled
        self.is_webchat_preview_enabled = is_webchat_preview_enabled
        self.is_token_enabled = is_token_enabled
        self.e_tag = e_tag


# This file is used for handwritten extensions to the generated code. Example:
# https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/customize_code/how-to-patch-sdk-code.md
def patch_sdk():
    curr_package = importlib.import_module("azure.mgmt.botservice")
    curr_package.models.WebChatSite = WebChatSite
    curr_package.models.DirectLineSite = DirectLineSite
    curr_package.models.Site = Site
