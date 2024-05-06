# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access
from typing import Any
from azure.ai.ml._utils._experimental import experimental

# Dev note: Supposedly there's going to be more artifact subclasses at some point.
# If/when that comes to pass, we can worry about adding polymorphism to these classes.
# For now, this is a one-off that's needed to help match the object structure that PF uses.


# Why is this not called a "LakeHouseArtifact"?  Because despite the under-the-hood type,
# users expect this variety to be called "OneLake".
@experimental
class OneLakeConnectionArtifact:
    """Artifact class used by the Connection subclass known
    as a MicrosoftOneLakeConnection. Supplying this class further
    specifies the connection as a Lake House connection.
    """

    # Note: Kwargs exist just to silently absorb type from schema.
    def __init__(self, *, name: str, **kwargs: Any):  # pylint: disable=unused-argument
        self.name = name
        self.type = "lake_house"
