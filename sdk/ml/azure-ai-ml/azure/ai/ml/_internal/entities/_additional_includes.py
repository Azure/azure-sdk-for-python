# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from ...entities._component._additional_includes import AdditionalIncludes


class InternalAdditionalIncludes(AdditionalIncludes):
    """This class is kept for compatibility with mldesigner."""

    @property
    def code_path(self):
        return self.resolved_code_path
