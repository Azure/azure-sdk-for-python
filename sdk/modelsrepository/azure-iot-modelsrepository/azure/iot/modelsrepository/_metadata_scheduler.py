# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import logging

_LOGGER = logging.getLogger(__name__)


class RepositoryFeatures(object):
    def __init__(self, **kwargs):
        """
        :keyword expanded: Whether the repository supports expanded models.
        :paramtype expanded: bool
        :keyword index: Whether the repository has an index file.
        :paramtype index: bool
        """
        self.expanded = kwargs.get("expanded")
        self.index = kwargs.get("index")


class ModelsRepositoryMetadata(object):
    def __init__(self, **kwargs):
        """
        ModelsRepositoryMetadata is used to deserialize the contents
        of the Models Repository metadata file as defined by
        https://github.com/Azure/iot-plugandplay-models-tools/wiki/Publishing-Metadata.

        :keyword commitId: Current Commit Id used
        :paramtype commitId: str
        :keyword publishDateUtc: Publish Date
        :paramtype publishDateUtc: str
        :keyword sourceRepo: Source Repository name
        :paramtype sourceRepo: str
        :keyword totalModelCount: Total number of Models in Model Repository
        :paramtype totalModelCount: int
        :keyword features: Model Repository features
        :paramtype features: RepositoryFeatures
        """
        self.commit_id = kwargs.get("commitId")
        self.publish_date_utc = kwargs.get("publishDateUtc")
        self.source_repo = kwargs.get("sourceRepo")
        self.total_model_count = kwargs.get("totalModelCount")
        self.features = RepositoryFeatures(kwargs.get("features"))


class MetadataScheduler(object):
    def __init__(self, enabled=True):
        # type: (bool) -> None
        """ MetadataScheduler tracks when metadata should be fetched from a repository.

        :param enabled: Whether the scheduler should be enabled.
        :type enabled: bool
        """
        self._initial_fetch = True
        self._enabled = enabled

    def should_fetch_metadata(self):
        # type: () -> bool
        """Indicates whether the caller should fetch metadata."""
        return self._enabled and self._initial_fetch

    def mark_as_fetched(self):
        # type: () -> None
        """To be invoked by caller indicating repository metadata has been fetched."""
        if self._initial_fetch:
            self._initial_fetch = False
