# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from typing import Optional
from pathlib import Path


def method_signature_and_response_type_annotation_template(
    *,
    method_signature: str,
    response_type_annotation: str,
) -> str:
    return f"{method_signature} -> {response_type_annotation}:"


def extract_sample_name(file_path: str) -> str:
    file = file_path.split("specification")[-1]
    return Path(file).parts[-1].replace(".json", "")


def strip_end(namespace: str) -> str:
    return ".".join(namespace.split(".")[:-1])


def get_namespace_config(namespace: str, multiapi: bool) -> str:
    return strip_end(namespace) if multiapi else namespace


def get_namespace_from_package_name(package_name: Optional[str]) -> str:
    return (package_name or "").replace("-", ".")
