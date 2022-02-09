# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import json
import re
from typing import TYPE_CHECKING
from ._common import EXPANDED_JSON_FILE_EXT

if TYPE_CHECKING:
    # pylint: disable=unused-import,ungrouped-imports
    from typing import Any, Dict, List

class FetchModelResult(object):
    """
    The FetchResult class has the purpose of containing key elements of
    a Fetcher.fetch() operation including model definition, path and whether
    it was from an expanded (pre-calculated) fetch.
    """
    def __init__(self, definition, path):
        # type: (str, str) -> None
        self.definition = definition
        self.path = path

    @property
    def from_expanded(self):
        # type: () -> bool
        """If the model was expanded or not."""
        return self.path.lower().endswith(EXPANDED_JSON_FILE_EXT)

    def __repr__(self):
        # type: () -> str
        return "FetchModelResult(defintion={}, path={})".format(
            self.definition, self.path
        )[:1024]


class ModelMetadata(object):
    """The Model class is responsible for storing results from ModelQuery.parse_model()."""
    def __init__(
        self,
        dtmi="",
        extends=None,
        components=None,
    ):
        # type: (str, List[str | ModelMetadata], List[str | ModelMetadata]) -> None
        """
        :param dtmi: The DTMI for the model
        :type dtmi: str
        :param extends: The list of strings or models representing the extend
        :type extends: list[str or ModelMetadata]
        :param components: The list of strings or models representing the components
        :type components: list[str or ModelMetadata]
        """
        self.dtmi = dtmi
        self.extends = extends if extends else []
        self.components = components if components else []
        self.dependencies = list(set(extends).union(set(components)))

    def __repr__(self):
        # type: () -> str
        return "ModelMetadata(dtmi={}, extends={}, components={})".format(
            self.dtmi, repr(self.extends), repr(self.components)
        )[:1024]


class ModelsRepositoryMetadata(object):
    # pylint:disable=too-many-instance-attributes
    """
    ModelsRepositoryMetadata is used to deserialize the contents
    of the Models Repository metadata file as defined by
    https://github.com/Azure/iot-plugandplay-models-tools/wiki/Publishing-Metadata.
    """
    def __init__(self, commit_id, publish_date_utc, source_repo, total_model_count, **kwargs):
        # type: (str, str, str, int, Any) -> None
        """
        :param commit_id: The latest commit id for the Models Repository
        :type commit_id: str
        :param publish_date_utc: The publish date of the Models Repository in UTC
        :type publish_date_utc: str
        :param source_repo: The location of the Models Repository
        :type source_repo: str
        :param total_model_count: Total number of models in the Models Repository
        :type total_model_count: int
        """
        self.commit_id = commit_id
        self.publish_date_utc = publish_date_utc
        self.source_repo = source_repo
        self.total_model_count = total_model_count
        features = kwargs.get("features")
        if isinstance(features, RepositoryFeatures):
            self.features = features
        else:
            self.features = RepositoryFeatures(**features)

    def __repr__(self):
        # type: () -> str
        return (
            "ModelsRepositoryMetadata(commitId={}, publishDateUtc={}, sourceRepo={}, "
            "totalModelCount={}, features={})".format(
                self.commit_id,
                self.publish_date_utc,
                self.source_repo,
                self.total_model_count,
                repr(self.features)
            )[:1024]
        )

    @classmethod
    def from_json_str(cls, json_str):
        # type: (str) -> ModelsRepositoryMetadata
        """Convert the contents of a metadata file to ModelsRepositoryMetadata.

        :param str json_str: metadata file contents

        :returns: ModelsRepositoryMetadata
        :rtype: ModelsRepositoryMetadata
        """
        # Remove trailing commas if needed
        json_str = re.sub(r",[ \t\r\n]+}", "}", json_str)
        json_str = re.sub(r",[ \t\r\n]+\]", "]", json_str)
        content = json.loads(json_str)
        return cls(
            commit_id=content.get("commitId"),
            publish_date_utc=content.get("publishDateUtc"),
            source_repo=content.get("sourceRepo"),
            total_model_count=content.get("totalModelCount"),
            features=content.get("features")
        )


class ModelResult(object):
    """Type encompassing repository fetched digital twin model content."""
    def __init__(self, content):
        # type: (Dict[str, str]) -> None
        self.content = content

    def __repr__(self):
        # type: () -> str
        return "ModelResult(content={})".format(
            repr(self.content)
        )[:1024]


class RepositoryFeatures(object):
    """
    RepositoryFeatures is part of ModelsRepositoryMetadata, which is used to
    deserialize the contents of the Models Repository metadata file as defined by
    https://github.com/Azure/iot-plugandplay-models-tools/wiki/Publishing-Metadata.
    """
    def __init__(self, **kwargs):
        # type: (Any) -> None
        """
        :keyword bool expanded: If expanded jsons are avaliable in the Models Repository
        :keywork bool index: If index is enabled for the Model Repository
        """
        self.expanded = kwargs.get("expanded", False)
        self.index = kwargs.get("index", False)

    def __repr__(self):
        # type: () -> str
        return "RepositoryFeatures(expanded={}, index={})".format(
            self.expanded, self.index
        )[:1024]
