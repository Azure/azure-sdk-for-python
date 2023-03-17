# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from datetime import datetime
from testcase import FarmBeatsPowerShellPreparer, FarmBeatsTestCase
from isodate.tzinfo import Utc
from devtools_testutils import recorded_by_proxy
from urllib.parse import urlparse, parse_qs


class TestFarmBeatsSatelliteJob(FarmBeatsTestCase):

    @FarmBeatsPowerShellPreparer()
    @recorded_by_proxy
    def test_satellite_flow(self, **kwargs):
        agrifood_endpoint = kwargs.pop("agrifood_endpoint")

        # Setup data
        party_id = "test-party-39735"
        common_id_prefix = "satellite-flow-asdf"
        boundary_id = common_id_prefix + "test-boundary"
        job_id = common_id_prefix + "job-47453"

        start_date_time = datetime(2020, 1, 1, tzinfo=Utc())
        end_date_time = datetime(2020, 1, 31, tzinfo=Utc())

        # Setup client
        client = self.create_client(agrifood_endpoint=agrifood_endpoint)

        # Create party
        party = client.parties.create_or_update(
            party_id=party_id,
            party={}
        )

        # Create boundary if not exists
        boundary = client.boundaries.create_or_update(
            party_id=party_id,
            boundary_id=boundary_id,
            boundary={
                "geometry":
                {
                    "type": "Polygon",
                    "coordinates":
                        [
                            [
                                [73.70457172393799, 20.545385304358106],
                                [73.70457172393799, 20.545385304358106],
                                [73.70448589324951, 20.542411534243367],
                                [73.70877742767334, 20.541688176010233],
                                [73.71023654937744, 20.545083911372505],
                                [73.70663166046143, 20.546992723579137],
                                [73.70457172393799, 20.545385304358106],
                            ]
                        ]
                },
                "status": "<string>",
                "name": "<string>",
                "description": "<string>"
            }
        )

        # Create satellite job
        satellite_job_poller = client.scenes.begin_create_satellite_data_ingestion_job(
            job_id=job_id,
            job={
                "boundaryId": boundary_id,
                "endDateTime": end_date_time,
                "partyId": party_id,
                "startDateTime": start_date_time,
                "provider": "Microsoft",
                "source": "Sentinel_2_L2A",
                "data": {
                    "imageNames": [
                        "NDVI"
                    ],
                    "imageFormats": [
                        "TIF"
                    ],
                    "imageResolution": [10]
                },
                "name": "<string>",
                "description": "<string>"
            }
        )
        satellite_job_poller.result()

        # Get terminal job state and assert
        assert satellite_job_poller.status() == "Succeeded"

        # Get scenes which are available in FarmBeats for our party and boundary of intrest.
        scenes = client.scenes.list(
            party_id=party_id,
            boundary_id=boundary_id,
            start_date_time=start_date_time,
            end_date_time=end_date_time,
            provider="Microsoft",
            source="Sentinel_2_L2A"
        )

        scenes_list = list(scenes)

        # Assert scenes got created
        assert len(scenes_list) == 12

        # Download scene file
        file_path = parse_qs(urlparse(scenes_list[0]["imageFiles"][0]["fileLink"]).query)['filePath'][0]
        file_iter = client.scenes.download(file_path=file_path)
        file = list(file_iter)
        assert len(file) == 3
