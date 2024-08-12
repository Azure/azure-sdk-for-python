import functools

from devtools_testutils import AzureRecordedTestCase, EnvironmentVariableLoader, recorded_by_proxy

from spatiopackage import AzureOrbitalPlanetaryComputerClient

SpatioPreparer = functools.partial(
    EnvironmentVariableLoader,
    "spatio",
    spatio_endpoint="https://micerutest.gkefbud8evgraxeq.uksouth.geocatalog.ppe.spatio.azure-test.net",
    spatio_group="fakegroup",
)


# The test class name needs to start with "Test" to get collected by pytest
class TestAzureOrbitalPlanetaryComputerClient(AzureRecordedTestCase):

    @classmethod
    def whatever(cls):
        credential = cls.get_credential(AzureOrbitalPlanetaryComputerClient)

    # Start with any helper functions you might need, for example a client creation method:
    def create_aopc_client(self, endpoint):
        credential = self.get_credential(AzureOrbitalPlanetaryComputerClient)
        aopc_client = AzureOrbitalPlanetaryComputerClient(endpoint=endpoint, credential=credential)
        return aopc_client

    ...

    # Write your test cases, each starting with "test_":
    @SpatioPreparer()
    @recorded_by_proxy
    def test_client_creation(self, spatio_endpoint):
        client = self.create_aopc_client(spatio_endpoint)
        assert client is not None
