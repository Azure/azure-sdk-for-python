from ._generated.dpsclient import AzureAgFoodPlatformDataPlaneService
from azure.identity import ClientSecretCredential

from .apigroupclients import (
    FarmerClient,
    FarmClient,
    FieldClient,
    BoundaryClient,
    JobClient,
    WeatherClient,
    SceneClient
)

class FarmbeatsClient():
    def __init__(
        self,
        instance_url,
        tenant_id,
        client_id,
        client_secret,

        # Optional
        authority="https://login.microsoftonline.com",
        scope="https://farmbeats.azure.net/.default",
    ):
        self.credential = ClientSecretCredential(
            tenant_id=tenant_id,
            client_id=client_id,
            client_secret=client_secret,
            authority=authority
        )

        self.client = AzureAgFoodPlatformDataPlaneService(
            credential=self.credential,
            credential_scopes=[scope],
            base_url=instance_url
        )

        self.farmers = FarmerClient(self.client)
        self.farms = FarmClient(self.client)
        self.fields = FieldClient(self.client)
        self.boundaries = BoundaryClient(self.client)
        self.jobs = JobClient(self.client)
        self.weatherdata = WeatherClient(self.client)
        self.scenes = SceneClient(self.client, self.credential)
