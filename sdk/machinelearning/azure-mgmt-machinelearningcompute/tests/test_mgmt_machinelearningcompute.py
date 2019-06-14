from azure.mgmt.resource import ResourceManagementClient
from devtools_testutils import AzureMgmtTestCase, ResourceGroupPreparer, AzureMgmtPreparer
from devtools_testutils.resource_testcase import RESOURCE_GROUP_PARAM
from azure.mgmt.machinelearningcompute import models, MachineLearningComputeManagementClient

NAME_PREFIX = 'mlcrp-python-test'
RESOURCE_GROUP_LOCATION = 'eastus2'

class OperationalizationClusterPreparer(AzureMgmtPreparer):
    def __init__(self, name_prefix='', location='East US 2 EUAP', cluster_type='ACS',
                 description='Deployed for testing.', orchestrator_type='Kubernetes',
                 random_name_length=24, resource_group_parameter_name=RESOURCE_GROUP_PARAM,
                 parameter_name='cluster_name', disable_recording=True,
                 playback_fake_resource=None):
        super(OperationalizationClusterPreparer, self).__init__(name_prefix,
                                                                random_name_length,
                                                                disable_recording=disable_recording,
                                                                playback_fake_resource=playback_fake_resource)
        self.location = location
        self.cluster_type = cluster_type
        self.description = description
        self.orchestrator_type = orchestrator_type
        self.resource_group_parameter_name = resource_group_parameter_name
        self.parameter_name = parameter_name

    def create_resource(self, name, **kwargs):
        if self.is_live:
            self.client = self.create_mgmt_client(MachineLearningComputeManagementClient)
            group = self._get_resource_group(**kwargs)

            from devtools_testutils.mgmt_settings_real import CLIENT_ID, CLIENT_SECRET

            temp_cluster_properties = models.OperationalizationCluster(
                location = self.location,
                cluster_type = self.cluster_type,
                description = self.description,
                container_service = models.AcsClusterProperties(
                    orchestrator_type = self.orchestrator_type,
                    orchestrator_properties = models.KubernetesClusterProperties(
                        service_principal = models.ServicePrincipalProperties(
                            client_id = CLIENT_ID,
                            secret = CLIENT_SECRET
                        )
                    )
                )
            )

            self.client.operationalization_clusters.create_or_update(group.name, name, 
                                                                     temp_cluster_properties).result()

        return {self.parameter_name: name}

    def remove_resource(self, name, **kwargs):
        if self.is_live:
            group = self._get_resource_group(**kwargs)
            self.client.operationalization_clusters.delete(group.name, name)

    def _get_resource_group(self, **kwargs):
        try:
            return kwargs.get(self.resource_group_parameter_name)
        except KeyError:
            template = 'To create an operationalization cluster a resource group is required. ' \
                       'Please add decorator @{} in front of this storage account preparer.'
            raise AzureTestError(template.format(ResourceGroupPreparer.__name__))


class MgmtMachineLearningComputeTest(AzureMgmtTestCase):
    FILTER_HEADERS = AzureMgmtTestCase.FILTER_HEADERS + ["strict-transport-security"]

    def setUp(self):
        super(MgmtMachineLearningComputeTest, self).setUp()
        self.client = self.create_mgmt_client(MachineLearningComputeManagementClient)

    @ResourceGroupPreparer(name_prefix=NAME_PREFIX + '-get', location=RESOURCE_GROUP_LOCATION, parameter_name='group')
    @OperationalizationClusterPreparer(name_prefix=NAME_PREFIX + '-get',
                                       resource_group_parameter_name='group')
    def test_get(self, group, cluster_name):
        fetched_cluster = self.client.operationalization_clusters.get(group.name, cluster_name)
        self.assertEqual(fetched_cluster.name, cluster_name)

    @ResourceGroupPreparer(name_prefix=NAME_PREFIX + '-keys', location=RESOURCE_GROUP_LOCATION, parameter_name='group')
    @OperationalizationClusterPreparer(name_prefix=NAME_PREFIX + '-keys',
                                       resource_group_parameter_name='group')
    def test_list_keys(self, group, cluster_name):
        keys = self.client.operationalization_clusters.list_keys(group.name, cluster_name)

        self.assertIsNotNone(keys.storage_account.resource_id)
        self.assertIsNotNone(keys.storage_account.primary_key)
        self.assertIsNotNone(keys.storage_account.secondary_key)
        self.assertIsNotNone(keys.container_registry.login_server)
        self.assertIsNotNone(keys.container_registry.password)
        self.assertIsNotNone(keys.container_registry.password2)
        self.assertIsNotNone(keys.container_service.acs_kube_config)
        self.assertIsNotNone(keys.container_service.image_pull_secret_name)

    @ResourceGroupPreparer(name_prefix=NAME_PREFIX + '-list', location=RESOURCE_GROUP_LOCATION, parameter_name='group')
    @OperationalizationClusterPreparer(name_prefix=NAME_PREFIX + '-list',
                                       resource_group_parameter_name='group')
    def test_list_clusters(self, group, cluster_name):
        clusters_in_resource_group = [c.name for c in list(self.client.operationalization_clusters.list_by_resource_group(group.name))]
        self.assertTrue(cluster_name in clusters_in_resource_group)

        clusters_in_subscription = [c.name for c in list(self.client.operationalization_clusters.list_by_subscription_id())]
        self.assertTrue(cluster_name in clusters_in_subscription)

    @ResourceGroupPreparer(name_prefix=NAME_PREFIX + '-delete', location=RESOURCE_GROUP_LOCATION, parameter_name='group')
    @OperationalizationClusterPreparer(name_prefix=NAME_PREFIX + '-delete',
                                       resource_group_parameter_name='group')
    def test_delete(self, group, cluster_name):
        self.client.operationalization_clusters.delete(group.name, cluster_name).result()
        clusters_in_subscription = [c.name for c in list(self.client.operationalization_clusters.list_by_subscription_id())]

        self.assertTrue(cluster_name not in clusters_in_subscription)

    @ResourceGroupPreparer(name_prefix=NAME_PREFIX + '-update', location=RESOURCE_GROUP_LOCATION, parameter_name='group')
    @OperationalizationClusterPreparer(name_prefix=NAME_PREFIX + '-update',
                                       resource_group_parameter_name='group')
    def test_system_services_update(self, group, cluster_name):
        updates_available = self.client.operationalization_clusters.check_system_services_updates_available(group.name, cluster_name)        
        self.assertIsNotNone(updates_available)

        update_result = self.client.operationalization_clusters.update_system_services(group.name, cluster_name).result()
        self.assertEqual("Succeeded", update_result.update_status)
        self.assertIsNotNone(update_result.update_started_on)
        self.assertIsNotNone(update_result.update_completed_on)

        updates_available = self.client.operationalization_clusters.check_system_services_updates_available(group.name, cluster_name)
        self.assertEqual("No", updates_available.updates_available)
