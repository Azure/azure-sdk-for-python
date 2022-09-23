# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import enum


class LocalEndpointMode(enum.Enum):
    ### This determines the mode of how the LocalEndpoint container will be created.
    ###
    DetachedContainer = 0
    VSCodeDevContainer = 1
