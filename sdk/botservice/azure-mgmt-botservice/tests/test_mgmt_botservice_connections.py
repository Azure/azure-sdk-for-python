import unittest

from devtools_testutils import AzureMgmtTestCase, ResourceGroupPreparer
from azure.mgmt.botservice import AzureBotService
from azure.mgmt.botservice.models import (
    Bot,
    BotProperties,
    Sku
)

class BotServiceConnectionsTestCase(AzureMgmtTestCase):
    def setUp(self):
        super(BotServiceConnectionsTestCase, self).setUp()
        #create a bot here
        self.client = self.create_mgmt_client(AzureBotService)
        self.resource_name = self.get_resource_name('azurebot')
    
    def createBot(self):
        location = 'global'
        sku_name = 'Free'
        kind= 'Bot'
        display_name = "this is a test bot"
        description= "this is a description for a test bot"
        endpoint = "https://bing.com/messages/"
        msa_app_id = "056d9ad9-17a9-4cc7-aebb-43bf6f293a08"
        developer_app_insight_key = '59513bad-10a7-4d41-b4d0-b1c34c6af512'
        developer_app_insights_api_key = 'w24iw5ocbhcig71su7ibaj63hey5ieaozeuwdv11'
        developer_app_insights_application_id = 'cf03484e-3fdb-4b5e-9ad7-94bde32e5a11'
        bot = self.client.bots.create(
            resource_group_name = self.resource_group_name,
            resource_name = self.resource_name,
            parameters = Bot(
                location= location,
                sku = sku.Sku(name=sku_name),
                kind= kind,
                properties= BotProperties(
                    display_name = display_name,
                    description= description,
                    endpoint = endpoint,
                    msa_app_id = msa_app_id,
                    developer_app_insight_key = developer_app_insight_key,
                    developer_app_insights_api_key = developer_app_insights_api_key,
                    developer_app_insights_application_id = developer_app_insights_application_id,
                )
            )
        )
    
    def tearDown(self):
        super(BotServiceConnectionsTestCase, self).tearDown()


    @unittest.skip("skip")
    @ResourceGroupPreparer(name_prefix='python_conn')
    def test_bot_connection_operations(self, resource_group):
        self.resource_group_name = resource_group.name
        self.createBot()
        from azure.mgmt.botservice.models import ConnectionSetting, ConnectionSettingProperties, ConnectionSettingParameter
        connection_resource_name = self.get_resource_name('myconnection')
        # create a connection
        setting_payload = ConnectionSetting(
            location='global',
            properties=ConnectionSettingProperties(
                client_id='clientId',
                client_secret='clientSecret',
                scopes='read,write',
                service_provider_id='00ea67de-bfc6-4f45-9ede-083899596b7b',
                parameters=[ConnectionSettingParameter(key='key1', value='value1')]
            )
        )
        setting = self.client.bot_connection.create(
            resource_group_name=resource_group.name,
            resource_name=self.resource_name,
            connection_name=connection_resource_name,
            parameters=setting_payload
        )
        self.assertIsNotNone(setting)
        self.assertEqual(setting.properties.client_id, 'clientId')

        # get a connection
        setting = self.client.bot_connection.get(
            resource_group_name=resource_group.name,
            resource_name=self.resource_name,
            connection_name=connection_resource_name
        )
        self.assertIsNotNone(setting)
        #list all connections
        settings = self.client.bot_connection.list_by_bot_service(
            resource_group_name = resource_group.name,
            resource_name=self.resource_name
        )
        self.assertIsNotNone(setting)
        self.assertTrue(len(list(settings)) == 1)

        # delete a connection
        setting = self.client.bot_connection.delete(
            resource_group_name=resource_group.name,
            resource_name=self.resource_name,
            connection_name=connection_resource_name
        )
        with self.assertRaises(ErrorException):
            setting = self.client.bot_connection.get(
                resource_group_name=resource_group.name,
                resource_name=self.resource_name,
                connection_name=connection_resource_name
            )


    @unittest.skip("skip")
    def test_bot_connection_serviceproviders(self):
        service_provider_responses = self.client.bot_connection.list_service_providers()
        self.assertTrue(len(service_provider_responses.value) > 0)
