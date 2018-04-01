from devtools_testutils import AzureMgmtTestCase
from azure.mgmt.botservice import AzureBotService
from azure.mgmt.botservice.models import Bot, BotProperties,sku,BotChannel,ErrorException
from azure.mgmt.botservice.models import (
    Bot,
    BotProperties,
    BotChannel,
    ErrorException,
    sku
)
import pdb

class BotServiceChannelsTestCase(AzureMgmtTestCase):
    def setUp(self):
        super(BotServiceChannelsTestCase, self).setUp()
        #create a bot here
        self.client = self.create_mgmt_client(AzureBotService)
        self.resource_group_name = 'testpythonrg'
        self.resource_name = 'testpythonbot13'
        location = 'global'
        sku_name = 'Free'
        kind= 'Bot'
        display_name = "this is a test bot"
        description= "this is a description for a test bot"
        endpoint = "https://bing.com/messages/"
        msa_app_id = "41a220b9-6571-4f0b-bbd2-43f1c1d82f53"
        developer_app_insight_key = '59513bad-10a7-4d41-b4d0-b1c34c6af52a'
        developer_app_insights_api_key = 'w24iw5ocbhcig71su7ibaj63hey5ieaozeuwdv2r'
        developer_app_insights_application_id = 'cf03484e-3fdb-4b5e-9ad7-94bde32e5a2b'
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

    def validateGetAndDeleteChannel(self, channel_name, channel_properties):
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

    # def test_email_channel(self):
    #     from azure.mgmt.botservice.models import EmailChannel,EmailChannelProperties
    #     channel = EmailChannel(
    #         properties = EmailChannelProperties(
    #             email_address = 'swagatm2@outlook.com',
    #             password = 'Redmond1!',
    #             is_enabled = True
    #         )
    #     )

    #     self.validateGetAndDeleteChannel(
    #         channel_name = 'EmailChannel',
    #         channel_properties = channel
    #     )

    # def test_msteams_channel(self):
    #     from azure.mgmt.botservice.models import MsTeamsChannel,MsTeamsChannelProperties
    #     channel = MsTeamsChannel(
    #         properties = MsTeamsChannelProperties(
    #             is_enabled = True, 
    #             enable_messaging = True, 
    #         )
    #     )
       
    #     self.validateGetAndDeleteChannel(
    #         channel_name = 'MsTeamsChannel',
    #         channel_properties = channel
    #     )
    
    # def test_skype_channel(self):
    #     from azure.mgmt.botservice.models import SkypeChannel,SkypeChannelProperties
    #     channel = SkypeChannel(
    #         properties = SkypeChannelProperties(
    #             is_enabled = True,
    #             enable_messaging = True,
    #         )
    #     )

    #     self.validateGetAndDeleteChannel(
    #         channel_name = 'SkypeChannel',
    #         channel_properties = channel
    #     )

    # def test_telegram_channel(self):
    #     from azure.mgmt.botservice.models import TelegramChannel,TelegramChannelProperties
    #     channel = TelegramChannel(
    #         properties = TelegramChannelProperties(
    #             access_token = '520413022:AAF12lBf6s4tSqntaXEZnvrn6XOVrjQ6YN4',
    #             is_enabled = True,
    #         )
    #     )

    #     self.validateGetAndDeleteChannel(
    #         channel_name = 'TelegramChannel',
    #         channel_properties = channel
    #     )

    # def test_sms_channel(self):
    #     from azure.mgmt.botservice.models import SmsChannel,SmsChannelProperties
    #     channel = SmsChannel(
    #         properties = SmsChannelProperties(
    #             phone = '+15153258725',
    #             account_sid = 'AC421cab6999e0c8c0d1a90c6643db8f05',
    #             auth_token = '507d2f4f9a832fdd042d05c500b3a88f',
    #             is_enabled = True,
    #             is_validated = False 
    #         )
    #     )
    
    #     self.validateGetAndDeleteChannel(
    #         channel_name = 'SmsChannel',
    #         channel_properties = channel
    #     )

    # def test_webchat_channel(self):
    #     from azure.mgmt.botservice.models import WebChatChannel,WebChatChannelProperties,WebChatSite
    #     channel = WebChatChannel(
    #         properties = WebChatChannelProperties(
    #             sites = [WebChatSite(
    #                 site_name = 'Default',
    #                 is_enabled = True,
    #                 enable_preview = True
    #             )]
    #         )
    #     )
        
    #     self.validateGetAndDeleteChannel(
    #         channel_name = 'WebChatChannel',
    #         channel_properties = channel
    #     )

    # def test_directline_channel(self):
    #     from azure.mgmt.botservice.models import DirectLineChannel,DirectLineChannelProperties,DirectLineSite
    #     channel = DirectLineChannel(
    #         properties = DirectLineChannelProperties(
    #             sites = [DirectLineSite(
    #                 site_name = 'Default',
    #                 is_enabled = True,
    #                 is_v1_enabled = False,
    #                 is_v3_enabled = True
    #             )]
    #         )
    #     )
        
    #     self.validateGetAndDeleteChannel(
    #         channel_name = 'DirectLineChannel',
    #         channel_properties = channel
    #     )