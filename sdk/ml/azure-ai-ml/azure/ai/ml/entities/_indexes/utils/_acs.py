# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Functions for interacting with AzureSearch."""

import functools
from importlib.util import find_spec, module_from_spec
from packaging import version as pkg_version


def _get_azuresearch_module_instance(langchain_package_version: pkg_version.Version):
    import langchain_core.pydantic_v1

    original_root_validator = langchain_core.pydantic_v1.root_validator
    try:
        langchain_core.pydantic_v1.root_validator = functools.partial(langchain_core.pydantic_v1.root_validator, allow_reuse=True)
        module_spec_name = 'langchain.vectorstores.azuresearch'
        if (langchain_package_version >= pkg_version.parse("0.1.00")):
            module_spec_name = 'langchain_community.vectorstores.azuresearch'
        module_spec = find_spec(module_spec_name)
        azuresearch = module_from_spec(module_spec)
        module_spec.loader.exec_module(azuresearch)
        print("hello")

        del azuresearch.AzureSearchVectorStoreRetriever

        return azuresearch
    finally:
        langchain_core.pydantic_v1.root_validator = original_root_validator
