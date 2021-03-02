import os
from datetime import datetime, timezone


class TestData:
    def __init__(self):
        self.account_endpoint = os.getenv("AZURE_ACCOUNT_ENDPOINT")
        self.instance_id = os.getenv("AZURE_INSTANCE_ID")

        self.provider = "Contoso"
        self.model = "Virtual-Machine"
        self.version = os.getenv("AZURE_UPDATE_VERSION")
        self.operation_id = os.getenv("AZURE_UPDATE_OPERATION")
        self.device_id = os.getenv("AZURE_DEVICE_ID")
        self.deployment_id = os.getenv("AZURE_DEPLOYMENT_ID")
        self.device_class_id = "b83e3c87fbf98063c20c3269f1c9e58d255906dd"
