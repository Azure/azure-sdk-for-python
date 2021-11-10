# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: mediacomposition_sample.py
DESCRIPTION:
    These samples demonstrate creating a user, issuing a token, revoking a token and deleting a user.

USAGE:
    python mediacomposition_samples.py
"""
import os
from azure.core import PipelineClient
from msrest import Deserializer, Serializer

class CommunicationMediaCompositionClientSamples(object):
    def create_media_composition_client(self):
        from azure.communication.mediacomposition._generated._configuration import (
            CommunicationMediaCompositionClientConfiguration
        )
        from azure.communication.mediacomposition._generated.operations import (
            MediaCompositionOperations
        )
        from azure.communication.mediacomposition._generated.models import _models

        base_url = 'http://localhost:57105'
        self._config = CommunicationMediaCompositionClientConfiguration()
        self._client = PipelineClient(base_url=base_url, config=self._config)

        client_models = {k: v for k, v in _models.__dict__.items() if isinstance(v, type)}
        self._serialize = Serializer(client_models)
        self._serialize.client_side_validation = False
        self._deserialize = Deserializer(client_models)

        media_composition_client = MediaCompositionOperations(
            self._client, self._config, self._serialize, self._deserialize)
        return media_composition_client

    def create_media_composition(self):
        from azure.communication.mediacomposition._generated.models import (
            CommunicationUserIdentifierModel,
            Layout,
            LayoutType,
            MediaCompositionBody,
            MediaInput,
            MediaOutput,
            MediaType,
            Resolution,
            Source,
            SourceType,
            TeamsMeeting
        )

        media_composition_client = self.create_media_composition_client()
        media_composition = MediaCompositionBody()
        media_composition_id = "WarholMediaComposition"
        media_composition.id = media_composition_id

        "Add media inputs"
        media_input = MediaInput()
        media_input.media_type = MediaType.TEAMS_MEETING
        teams_meeting = TeamsMeeting()
        teams_meeting.teams_join_url = "REPLACE_WITH_TEAMS_JOIN_URL"
        media_input.teams_meeting = teams_meeting
        media_inputs = {}
        media_inputs["watchParty"] = media_input
        media_composition.media_inputs = media_inputs

        "Add sources"
        source = Source()
        source.source_type = SourceType.PARTICIPANT
        source.media_input_id = "watchParty"
        source.participant = CommunicationUserIdentifierModel()
        source.participant.id = "REPLACE_WITH_PARTICIPANT_ID"
        sources = {}
        sources["presenter"] = source
        media_composition.sources = sources

        "Add layout"
        layout = Layout()
        layout.type = LayoutType.WARHOL
        layout.resolution = Resolution()
        layout.resolution.width = 1920
        layout.resolution.height = 1080
        media_composition.layout = layout

        "Add media outputs"
        media_output = MediaOutput()
        media_output.media_type = MediaType.TEAMS_MEETING
        media_output.teams_meeting = teams_meeting
        media_outputs = {}
        media_outputs["teams"] = media_output
        media_composition.media_outputs = media_outputs

        media_composition_client.create(media_composition_id, media_composition)

    def start_media_composition(self, media_composition_id):
        media_composition_client = self.create_media_composition_client()
        media_composition_client.start(media_composition_id)

    def stop_media_composition(self, media_composition_id):
        media_composition_client = self.create_media_composition_client()
        media_composition_client.stop(media_composition_id)

if __name__ == '__main__':
    sample = CommunicationMediaCompositionClientSamples()
    sample.create_media_composition_client()
    sample.create_media_composition()
    sample.start_media_composition("WarholMediaComposition")
    sample.stop_media_composition("WarholMediaComposition")
