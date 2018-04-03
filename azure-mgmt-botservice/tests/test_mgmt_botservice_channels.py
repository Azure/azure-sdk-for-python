from devtools_testutils import AzureMgmtTestCase, ResourceGroupPreparer
from azure.mgmt.botservice import AzureBotService
from azure.mgmt.botservice.models import (
    Bot,
    BotProperties,
    BotChannel,
    ErrorException,
    sku
)

class BotServiceChannelsTestCase(AzureMgmtTestCase):
    def setUp(self):
        super(BotServiceChannelsTestCase, self).setUp()
        #create a bot here
        self.client = self.create_mgmt_client(AzureBotService)
        self.resource_name = self.get_resource_name('azurebotservice')
    
    def createBot(self):
        location = 'global'
        sku_name = 'Free'
        kind= 'Bot'
        display_name = "this is a test bot"
        description= "this is a description for a test bot"
        endpoint = "https://bing.com/messages/"
        msa_app_id = "056d9ad9-17a9-4cc7-aebb-43bf6f293a08"
        developer_app_insight_key = '59513bad-10a7-4d41-b4d0-b1c34c6af511'
        developer_app_insights_api_key = 'w24iw5ocbhcig71su7ibaj63hey5ieaozeuwdv11'
        developer_app_insights_application_id = 'cf03484e-3fdb-4b5e-9ad7-94bde32e5a11'
        bot = self.client.bots.create(
            resource_group_name = self.resource_group_name,
            resource_name = self.resource_name,
            parameters = Bot(
                location= location,
                sku = sku.Sku(sku_name),
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
        super(BotServiceChannelsTestCase, self).tearDown()
        self.client.bots.delete(
            resource_group_name = self.resource_group_name,
            resource_name = self.resource_name
        )

    def validateCreateGetAndDeleteChannel(self, channel_name, channel_properties):
        self.createBot()

        botChannel = BotChannel(
            location = 'global',
            properties = channel_properties
        )

        self.client.channels.create(
            resource_group_name = self.resource_group_name,
            resource_name = self.resource_name,
            channel_name = channel_name,
            parameters = botChannel 
        )

        channel = self.client.channels.get(
            resource_group_name = self.resource_group_name,
            resource_name = self.resource_name,
            channel_name = channel_name
        )
        
        self.assertIsNotNone(channel)
        #is_enabled being true means that the service has managed to get the channel working.
        if channel_name == 'DirectLineChannel':
            self.assertTrue(channel.properties.properties.sites[0].is_enabled)
        else:
            self.assertTrue(channel.properties.properties.is_enabled)

        channel = self.client.channels.delete(
            resource_group_name = self.resource_group_name,
            resource_name = self.resource_name,
            channel_name = channel_name
        )
        with self.assertRaises(ErrorException):
            channel = self.client.channels.get(
                resource_group_name = self.resource_group_name,
                resource_name = self.resource_name,
                channel_name = channel_name
            )

    @ResourceGroupPreparer(name_prefix='pythonsdkbot')
    def test_email_channel(self, resource_group):
        self.resource_group_name = resource_group.name
        from azure.mgmt.botservice.models import EmailChannel,EmailChannelProperties
        channel = EmailChannel(
            properties = EmailChannelProperties(
                email_address = 'swagatm2@outlook.com',
                password = 'Botuser123@',
                is_enabled = True
            )
        )

        self.validateCreateGetAndDeleteChannel(
            channel_name = 'EmailChannel',
            channel_properties = channel
        )

    # @ResourceGroupPreparer(name_prefix='pythonsdkbot')
    # def test_msteams_channel(self, resource_group):
    #     from azure.mgmt.botservice.models import MsTeamsChannel,MsTeamsChannelProperties
    #     self.resource_group_name = resource_group.name
    #     channel = MsTeamsChannel(
    #         properties = MsTeamsChannelProperties(
    #             is_enabled = True, 
    #             enable_messaging = True, 
    #         )
    #     )
       
    #     self.validateCreateGetAndDeleteChannel(
    #         channel_name = 'MsTeamsChannel',
    #         channel_properties = channel
    #     )
    
    # @ResourceGroupPreparer(name_prefix='pythonsdkbot')
    # def test_skype_channel(self, resource_group):
    #     from azure.mgmt.botservice.models import SkypeChannel,SkypeChannelProperties
        # self.resource_group_name = resource_group.name
    #     channel = SkypeChannel(
    #         properties = SkypeChannelProperties(
    #             is_enabled = True,
    #             enable_messaging = True,
    #         )
    #     )

    #     self.validateCreateGetAndDeleteChannel(
    #         channel_name = 'SkypeChannel',
    #         channel_properties = channel
    #     )

    @ResourceGroupPreparer(name_prefix='pythonsdkbot')
    def test_telegram_channel(self, resource_group):
        from azure.mgmt.botservice.models import TelegramChannel,TelegramChannelProperties
        self.resource_group_name = resource_group.name
        channel = TelegramChannel(
            properties = TelegramChannelProperties(
                access_token = '520413022:AAF12lBf6s4tSqntaXEZnvrn6XOVrjQ6YN4',
                is_enabled = True,
            )
        )

        self.validateCreateGetAndDeleteChannel(
            channel_name = 'TelegramChannel',
            channel_properties = channel
        )

    @ResourceGroupPreparer(name_prefix='pythonsdkbot')
    def test_sms_channel(self, resource_group):
        from azure.mgmt.botservice.models import SmsChannel,SmsChannelProperties
        self.resource_group_name = resource_group.name
        channel = SmsChannel(
            properties = SmsChannelProperties(
                phone = '+15153258725',
                account_sid = 'AC421cab6999e0c8c0d1a90c6643db8f05',
                auth_token = '507d2f4f9a832fdd042d05c500b3a88f',
                is_enabled = True,
                is_validated = False 
            )
        )
    
        self.validateCreateGetAndDeleteChannel(
            channel_name = 'SmsChannel',
            channel_properties = channel
        )
