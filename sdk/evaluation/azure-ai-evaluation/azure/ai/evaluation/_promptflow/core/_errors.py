# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from .. import PF_EXCEPTION_DEP_REMOVED
from ..exceptions import ErrorTarget, UserErrorException


MissingRequiredPackage = None


if (not PF_EXCEPTION_DEP_REMOVED):
    #TODO ralphe: Remove this block once the promptflow exception dependency is removed
    from promptflow.core._errors import MissingRequiredInputError as PF_MissingRequiredPackage
    MissingRequiredPackage = PF_MissingRequiredPackage

else:
    class _MissingRequiredPackage(UserErrorException):
        def __init__(self, **kwargs):
            super().__init__(target=ErrorTarget.CORE, **kwargs)

    MissingRequiredPackage = _MissingRequiredPackage