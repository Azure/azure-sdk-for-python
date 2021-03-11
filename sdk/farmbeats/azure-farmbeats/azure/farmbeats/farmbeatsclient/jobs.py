import time
from datetime import datetime, timedelta


class JobClient():
    def __init__(
        self,
        farmbeats_client
    ):
        self.client = farmbeats_client

    def queue_satellite_job(
        self,
        job,
    ):
        return self.client.create_satellite_job(
            job
        )

    def queue_weather_job(
        self,
        job,
        x_ms_farm_beats_data_provider_key,
        x_ms_farm_beats_data_provider_id=None,
    ):
        return self.client.create_weather_job(
            x_ms_farm_beats_data_provider_key,
            x_ms_farm_beats_data_provider_id,
            job
        )

    def get_job(
        self,
        job_id
    ):
        return self.client.get_job(
            job_id
        )

    def wait_for_job(
        self,
        job_id,
        timeout=300
    ):
        wait_start_time = datetime.now()
        print("Starting wait at ", wait_start_time)
        while True:

            if datetime.now() - wait_start_time > timedelta(seconds=timeout):
                print("Wait timed out at", datetime.now())
                return None

            job = self.get_job(job_id)
            if job.status not in ["Succeeded", "Failed"]:
                print(job.status)
                time.sleep(1)
            else:
                print("Job terminated with status:", job.status, "at", datetime.now())
                return job
