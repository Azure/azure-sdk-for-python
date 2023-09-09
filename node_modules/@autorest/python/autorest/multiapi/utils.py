# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import logging
from typing import Dict, List, Optional

_LOGGER = logging.getLogger(__name__)


def _sync_or_async(async_mode: bool) -> str:
    return "async" if async_mode else "sync"


def _get_default_api_version_from_list(
    mod_to_api_version: Dict[str, str],
    api_versions_list: List[str],
    preview_mode: bool,
    user_specified_default_api: Optional[str],
) -> str:
    """Get the floating latest, from a random list of API versions."""

    # I need user_specified_default_api to be v2019_06_07_preview shaped if it exists, let's be smart
    # and change it automatically so I can take both syntax as input
    if user_specified_default_api and not user_specified_default_api.startswith("v"):
        default_api_version = [
            mod_api
            for mod_api, real_api in mod_to_api_version.items()
            if real_api == user_specified_default_api
        ][0]
        _LOGGER.info("Default API version will be: %s", default_api_version)
        return default_api_version

    absolute_latest = sorted(api_versions_list)[-1]
    not_preview_versions = [
        version for version in api_versions_list if "preview" not in version
    ]

    # If there is no preview, easy: the absolute latest is the only latest
    if not not_preview_versions:
        return absolute_latest

    # If preview mode, let's use the absolute latest, I don't care preview or stable
    if preview_mode:
        return absolute_latest

    # If not preview mode, and there is preview, take the latest known stable
    return sorted(not_preview_versions)[-1]


def convert_list_to_tuple(l):
    if not isinstance(l, list):
        return l
    return tuple(convert_list_to_tuple(x) for x in l) if isinstance(l, list) else l
