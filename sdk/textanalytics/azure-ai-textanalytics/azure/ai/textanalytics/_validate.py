# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import functools
from ._version import VERSIONS_SUPPORTED


def check_for_unsupported_actions_types(*args, **kwargs):

    client = args[0]
    # this assumes the client has an _api_version attribute
    selected_api_version = client._api_version  # pylint: disable=protected-access

    if "actions" not in kwargs:
        actions = args[2]
    else:
        actions = kwargs.get("actions")

    if actions is None:
        return

    actions_version_mapping = {
        "2022-04-01-preview":
        [
            "ExtractSummaryAction",
            "RecognizeCustomEntitiesAction",
            "SingleCategoryClassifyAction",
            "MultiCategoryClassifyAction",
            "AnalyzeHealthcareEntitiesAction"
        ]
    }

    unsupported = {
        arg: version
        for version, args in actions_version_mapping.items()
        for arg in args
        if arg in [action.__class__.__name__ for action in actions]
           and selected_api_version != version
           and VERSIONS_SUPPORTED.index(selected_api_version) < VERSIONS_SUPPORTED.index(version)
    }

    if unsupported:
        error_strings = [
            f"'{param}' is only available for API version {version} and up.\n"
            for param, version in unsupported.items()
        ]
        raise ValueError("".join(error_strings))


def validate_multiapi_args(**kwargs):
    args_mapping = kwargs.pop("args_mapping", None)
    version_method_added = kwargs.pop("version_method_added", None)
    custom_wrapper = kwargs.pop("custom_wrapper", None)

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                # this assumes the client has an _api_version attribute
                client = args[0]
                selected_api_version = client._api_version  # pylint: disable=protected-access
            except AttributeError:
                return func(*args, **kwargs)

            # the latest version is selected, we assume all features supported
            if selected_api_version == VERSIONS_SUPPORTED[-1]:
                return func(*args, **kwargs)

            if version_method_added and version_method_added != selected_api_version and \
                    VERSIONS_SUPPORTED.index(selected_api_version) < VERSIONS_SUPPORTED.index(version_method_added):
                raise ValueError(f"'{func.__name__}' is only available for API version {version_method_added} and up.")

            if args_mapping:
                unsupported = {
                    arg: version
                    for version, args in args_mapping.items()
                    for arg in args
                    if arg in kwargs.keys()
                    and selected_api_version != version
                    and VERSIONS_SUPPORTED.index(selected_api_version) < VERSIONS_SUPPORTED.index(version)
                }
                if unsupported:
                    error_strings = [
                        f"'{param}' is only available for API version {version} and up.\n"
                        for param, version in unsupported.items()
                    ]
                    raise ValueError("".join(error_strings))

            if custom_wrapper:
                custom_wrapper(*args, **kwargs)

            return func(*args, **kwargs)

        return wrapper

    return decorator
