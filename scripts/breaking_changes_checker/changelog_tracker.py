#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from enum import Enum
from typing import Any, Dict
import jsondiff
from breaking_changes_tracker import BreakingChangesTracker

class ChangeType(str, Enum):
    ADDED_CLIENT = "AddedClient"
    ADDED_CLIENT_METHOD = "AddedClientMethod"
    ADDED_CLASS = "AddedClass"
    ADDED_CLASS_METHOD = "AddedClassMethod"
    ADDED_CLASS_METHOD_PARAMETER = "AddedClassMethodParameter"
    ADDED_CLASS_PROPERTY = "AddedClassProperty"
    ADDED_ENUM = "AddedEnum"
    ADDED_ENUM_MEMBER = "AddedEnumMember"
    ADDED_FUNCTION_PARAMETER = "AddedFunctionParameter"
    ADDED_OPERATION_GROUP = "AddedOperationGroup"

class ChangelogTracker(BreakingChangesTracker):
    ADDED_FUNCTION_PARAMETER_MSG = \
        "Function `{}` added parameter `{}`"


    def __init__(self, stable: Dict, current: Dict, package_name: str, **kwargs: Any) -> None:
        super().__init__(stable, current, package_name, **kwargs)
        self.features_added = []

    def run_checks(self) -> None:
        super().run_checks()
        self.run_async_cleanup(self.features_added)

    def report_changes(self) -> None:
        ignore_changes = self.ignore if self.ignore else {}
        self.get_reportable_changes(ignore_changes, self.breaking_changes)
        self.get_reportable_changes(ignore_changes, self.features_added)
        # Code borrowed and modified from the previous change log tool
        def _build_md(content: list, title: str, buffer: list):
            buffer.append(title)
            buffer.append("")
            for _, bc in enumerate(content):
                # Extract the message, skip the change type and the module name
                msg, _, _,*args = bc
                buffer.append("  - " + msg.format(*args))
            buffer.append("")
            return buffer

        buffer = []
        if self.features_added:
            _build_md(self.features_added, "### Features Added", buffer)
        if self.breaking_changes:
            _build_md(self.breaking_changes, "### Breaking Changes", buffer)
        content =  "\n".join(buffer).strip()

        content = "===== changelog start =====\n" + content + "\n===== changelog end =====\n"
        return content
