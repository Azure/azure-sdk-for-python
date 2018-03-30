from devtools_testutils import AzureMgmtTestCase
from azure.mgmt.botservice import AzureBotService
from azure.mgmt.botservice.models import Bot, BotProperties,sku
import json

class CoreBotServiceTestCase(AzureMgmtTestCase):
    def setUp(self):
        super(CoreBotServiceTestCase, self).setUp()
        self.client = self.create_mgmt_client(AzureBotService)
        self.resource_group_name = 'testpythonrg'
        self.resource_name = 'testpythonbot12'
        self.location = 'global'
        self.sku_name = 'F0'
        self.kind= 'Bot'
        self.display_name = "this is a test bot"
        self.description= "this is a description for a test bot"
        self.endpoint = "https://bing.com/messages/"
        self.msa_app_id = "41a220b9-6571-4f0b-bbd2-43f1c1d82f51"
        self.developer_app_insight_key = '59513bad-10a7-4d41-b4d0-b1c34c6af52a'
        self.developer_app_insights_api_key = 'w24iw5ocbhcig71su7ibaj63hey5ieaozeuwdv2r'
        self.developer_app_insights_application_id = 'cf03484e-3fdb-4b5e-9ad7-94bde32e5a2b'

    def validate_bot_properties(self, bot):
        self.assertEqual(bot.id, f'/subscriptions/{self.client.config.subscription_id}/resourceGroups/{self.resource_group_name}/providers/Microsoft.BotService/botServices/{self.resource_name}')
        self.assertEqual(bot.name, self.resource_name)
        self.assertEqual(bot.location, self.location)
        self.assertEqual(bot.sku.name, self.sku_name)
        self.assertEqual(bot.kind, self.kind)
        self.assertEqual(bot.properties.display_name, self.display_name)
        self.assertEqual(bot.properties.description, self.description)
        self.assertEqual(bot.properties.endpoint, self.endpoint)
        self.assertEqual(bot.properties.msa_app_id, self.msa_app_id)
        self.assertEqual(bot.properties.developer_app_insight_key, self.developer_app_insight_key)
        self.assertEqual(bot.properties.developer_app_insights_api_key, None) #this password should not be returned in the response
        self.assertEqual(bot.properties.developer_app_insights_application_id, self.developer_app_insights_application_id)

    def test_bot_operations(self):
        bot = self.client.bots.create(
            resource_group_name = self.resource_group_name,
            resource_name = self.resource_name,
            parameters = Bot(
                location= self.location,
                sku = sku.Sku(self.sku_name),
                kind= self.kind,
                properties= BotProperties(
                    display_name = self.display_name,
                    description= self.description,
                    endpoint = self.endpoint,
                    msa_app_id = self.msa_app_id,
                    developer_app_insight_key = self.developer_app_insight_key,
                    developer_app_insights_api_key = self.developer_app_insights_api_key,
                    developer_app_insights_application_id = self.developer_app_insights_application_id,
                )
            )
        )
        self.validate_bot_properties(bot)

        bot = self.client.bots.get(
            resource_group_name = self.resource_group_name,
            resource_name = self.resource_name,
        )
        self.validate_bot_properties(bot)

        bot.properties.description = 'this is another description'
        self.description = bot.properties.description
        bot = self.client.bots.update(
            resource_group_name = self.resource_group_name,
            resource_name = self.resource_name,
            properties = bot.properties
        )
        self.validate_bot_properties(bot)
        bot = self.client.bots.delete(
            resource_group_name = self.resource_group_name,
            resource_name = self.resource_name,
        )
        self.validate_bot_properties(bot)

        #ensure that the bot was not found with a get
        with self.assertRaises(ErrorException):
            bot = self.client.bots.get(
                resource_group_name = self.resource_group_name,
                resource_name = self.resource_name
            )
