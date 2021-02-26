# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from typing import TYPE_CHECKING
from datetime import date, datetime
import time

from azure.core.credentials import AzureKeyCredential, AccessToken

if TYPE_CHECKING:
    # pylint: disable=unused-import,ungrouped-imports
    from typing import Any

ACCOUNT_KEY_VALID_YEARS = 10

class MixedRealityAccountKeyCredential(object):
    """ Represents an object used for Mixed Reality account key authentication.

    :param str account_id: The Mixed Reality service account identifier.
    :param AzureKeyCredential account_key: The Mixed Reality service account primary or secondary key credential.
    """

    def __init__(self, account_id, account_key):
        # type: (str, AzureKeyCredential) -> None
        self.account_id = account_id
        self.account_key = account_key

    def get_token(self, *scopes, **kwargs): #pylint: disable=unused-argument
        # type: (*str, **Any) -> AccessToken

        token = self.account_id + ":" + self.account_key.key

        # No way to know when an account key might expire, so we'll set the
        # access token wrapping it to expire 10 years in the future.
        expiration_date = _add_years(datetime.now(), ACCOUNT_KEY_VALID_YEARS)
        expiration_timestamp = int(time.mktime(expiration_date.timetuple()))

        return AccessToken(token, expiration_timestamp)

def _add_years(date_to_update, years):
    try:
        return date_to_update.replace(year=date_to_update.year + years)
    except ValueError:
        return date_to_update + (date(date_to_update.year + years, 1, 1) - date(date_to_update.year, 1, 1))
