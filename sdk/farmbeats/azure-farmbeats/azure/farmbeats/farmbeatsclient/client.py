from ..dpsclient import AzureAgFoodPlatformDataPlaneService
from azure.identity import ClientSecretCredential

from .farmers import FarmerClient
from .farms import FarmClient
from .fields import FieldClient
from .boundaries import BoundaryClient
from .jobs import JobClient
from .weatherdata import WeatherDataClient
from .scenes import SceneClient

class Client():
    def __init__(
        self,
        instance_url,
        tenant_id,
        client_id,
        client_secret,

        # Optional
        # TODO change the default to prod.
        authority="https://login.windows-ppe.net",
        scope="https://farmbeats-dogfood.azure.net/.default",
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
        self.weatherdata = WeatherDataClient(self.client)
        self.scenes = SceneClient(self.client, self.credential)
