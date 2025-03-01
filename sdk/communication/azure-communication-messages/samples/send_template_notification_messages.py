# pylint: disable=line-too-long,useless-suppression
# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: send_template_notification_messages.py

DESCRIPTION:
    This sample demonstrates sending an Whatsapp template message from business phone number to a single user. 
    Template to be used in the sample needs to be created in WhatsApp Business account first.
    Follow the instructions in the Meta Business Help Center at https://www.facebook.com/business/help/2055875911147364?id=2129163877102343.
    The NotificationMessageClient is authenticated using a connection string.
USAGE:
    python send_template_notification_messages.py

    Set the environment variable with your own value before running the sample:
    1) COMMUNICATION_SAMPLES_CONNECTION_STRING - the connection string in your ACS resource
    2) RECIPIENT_PHONE_NUMBER - a phone number with Whatsapp capabilities. Use list for recipient phone number.
    3) WHATSAPP_CHANNEL_ID - Channel created in Azure portal for Advanced Messaging.
"""

import os
import sys

sys.path.append("..")


class SendWhatsAppTemplateMessageSample(object):

    connection_string = os.getenv("COMMUNICATION_SAMPLES_CONNECTION_STRING")
    phone_number = os.getenv("RECIPIENT_PHONE_NUMBER")
    channel_id = os.getenv("WHATSAPP_CHANNEL_ID")

    def send_template_send_message(self):

        from azure.communication.messages import NotificationMessagesClient
        from azure.communication.messages.models import TemplateNotificationContent, MessageTemplate

        messaging_client = NotificationMessagesClient.from_connection_string(self.connection_string)

        # Setting template options
        input_template: MessageTemplate = MessageTemplate(name="cpm_welcome", language="en_us")

        template_options = TemplateNotificationContent(
            channel_registration_id=self.channel_id, to=[self.phone_number], template=input_template
        )

        # calling send() with whatsapp message details
        message_responses = messaging_client.send(template_options)
        response = message_responses.receipts[0]
        print("Message with message id {} was successful sent to {}".format(response.message_id, response.to))

    def send_template_message_with_parameters(self):

        from azure.communication.messages import NotificationMessagesClient
        from azure.communication.messages.models import (
            TemplateNotificationContent,
            MessageTemplate,
            MessageTemplateText,
            WhatsAppMessageTemplateBindings,
            WhatsAppMessageTemplateBindingsComponent,
        )

        messaging_client = NotificationMessagesClient.from_connection_string(self.connection_string)

        # Setting template options
        templateName = "sample_shipping_confirmation"
        templateLanguage = "en_us"
        shippingConfirmationTemplate: MessageTemplate = MessageTemplate(name=templateName, language=templateLanguage)
        threeDays = MessageTemplateText(name="threeDays", text="3")
        bindings = WhatsAppMessageTemplateBindings(
            body=[WhatsAppMessageTemplateBindingsComponent(ref_value=threeDays.name)]
        )
        shippingConfirmationTemplate.bindings = bindings
        shippingConfirmationTemplate.template_values = [threeDays]
        template_options = TemplateNotificationContent(
            channel_registration_id=self.channel_id, to=[self.phone_number], template=shippingConfirmationTemplate
        )

        # calling send() with whatsapp message details
        message_responses = messaging_client.send(template_options)
        response = message_responses.receipts[0]
        print("Message with message id {} was successful sent to {}".format(response.message_id, response.to))

    def send_template_message_with_buttons(self):

        from azure.communication.messages import NotificationMessagesClient
        from azure.communication.messages.models import (
            TemplateNotificationContent,
            MessageTemplate,
            MessageTemplateText,
            WhatsAppMessageTemplateBindings,
            WhatsAppMessageTemplateBindingsComponent,
            MessageTemplateQuickAction,
            WhatsAppMessageTemplateBindingsButton,
            WhatsAppMessageButtonSubType,
        )

        messaging_client = NotificationMessagesClient.from_connection_string(self.connection_string)

        # Setting template options
        templateName = "sample_issue_resolution"
        templateLanguage = "en_us"
        shippingConfirmationTemplate: MessageTemplate = MessageTemplate(name=templateName, language=templateLanguage)
        name = MessageTemplateText(name="first", text="Joe")
        yes = MessageTemplateQuickAction(name="Yes", payload="Joe said yes")
        no = MessageTemplateQuickAction(name="No", payload="Joe said no")
        bindings = WhatsAppMessageTemplateBindings(body=[WhatsAppMessageTemplateBindingsComponent(ref_value=name.name)])
        bindings.buttons = [
            WhatsAppMessageTemplateBindingsButton(
                sub_type=WhatsAppMessageButtonSubType.QUICK_REPLY, ref_value=yes.name
            ),
            WhatsAppMessageTemplateBindingsButton(sub_type=WhatsAppMessageButtonSubType.QUICK_REPLY, ref_value=no.name),
        ]
        shippingConfirmationTemplate.bindings = bindings
        shippingConfirmationTemplate.template_values = [name, yes, no]
        template_options = TemplateNotificationContent(
            channel_registration_id=self.channel_id, to=[self.phone_number], template=shippingConfirmationTemplate
        )

        # calling send() with whatsapp message details
        message_responses = messaging_client.send(template_options)
        response = message_responses.receipts[0]
        print("Message with message id {} was successful sent to {}".format(response.message_id, response.to))

    def send_template_message_with_media(self):

        from azure.communication.messages import NotificationMessagesClient
        from azure.communication.messages.models import (
            TemplateNotificationContent,
            MessageTemplate,
            MessageTemplateText,
            WhatsAppMessageTemplateBindings,
            WhatsAppMessageTemplateBindingsComponent,
            MessageTemplateImage,
        )

        messaging_client = NotificationMessagesClient.from_connection_string(self.connection_string)

        # Setting template options
        templateName = "sample_movie_ticket_confirmation"
        templateLanguage = "en_us"
        imageUrl = "https://aka.ms/acsicon1"
        sample_movie_ticket_confirmation: MessageTemplate = MessageTemplate(
            name=templateName, language=templateLanguage
        )
        image = MessageTemplateImage(name="image", url=imageUrl)
        title = MessageTemplateText(name="title", text="Contoso")
        time = MessageTemplateText(name="time", text="July 1st, 2023 12:30PM")
        venue = MessageTemplateText(name="venue", text="Southridge Video")
        seats = MessageTemplateText(name="seats", text="Seat 1A")

        bindings = WhatsAppMessageTemplateBindings(
            header=[WhatsAppMessageTemplateBindingsComponent(ref_value=image.name)],
            body=[
                WhatsAppMessageTemplateBindingsComponent(ref_value=title.name),
                WhatsAppMessageTemplateBindingsComponent(ref_value=time.name),
                WhatsAppMessageTemplateBindingsComponent(ref_value=venue.name),
                WhatsAppMessageTemplateBindingsComponent(ref_value=seats.name),
            ],
        )

        sample_movie_ticket_confirmation.bindings = bindings
        sample_movie_ticket_confirmation.template_values = [image, title, time, venue, seats]
        template_options = TemplateNotificationContent(
            channel_registration_id=self.channel_id, to=[self.phone_number], template=sample_movie_ticket_confirmation
        )

        # calling send() with whatsapp message details
        message_responses = messaging_client.send(template_options)
        response = message_responses.receipts[0]
        print("Message with message id {} was successful sent to {}".format(response.message_id, response.to))

    def send_template_message_with_call_to_action(self):

        from azure.communication.messages import NotificationMessagesClient
        from azure.communication.messages.models import (
            TemplateNotificationContent,
            MessageTemplate,
            MessageTemplateText,
            WhatsAppMessageTemplateBindings,
            WhatsAppMessageTemplateBindingsComponent,
            MessageTemplateQuickAction,
            MessageTemplateImage,
            WhatsAppMessageTemplateBindingsButton,
            WhatsAppMessageButtonSubType,
        )

        messaging_client = NotificationMessagesClient.from_connection_string(self.connection_string)

        # Setting template options
        templateName = "purchase_feedback"
        templateLanguage = "en_us"
        imageUrl = "https://aka.ms/acsicon1"
        sample_purchase_feedback: MessageTemplate = MessageTemplate(name=templateName, language=templateLanguage)
        name = MessageTemplateText(name="first", text="Joe")
        image = MessageTemplateImage(name="image", url=imageUrl)
        uri_to_click = MessageTemplateQuickAction(name="url", text="questions")

        bindings = WhatsAppMessageTemplateBindings(
            body=[WhatsAppMessageTemplateBindingsComponent(ref_value=name.name)],
            header=[WhatsAppMessageTemplateBindingsComponent(ref_value=image.name)],
            buttons=[
                WhatsAppMessageTemplateBindingsButton(
                    sub_type=WhatsAppMessageButtonSubType.URL, ref_value=uri_to_click.name
                )
            ],
        )
        sample_purchase_feedback.bindings = bindings
        sample_purchase_feedback.template_values = [name, image, uri_to_click]
        template_options = TemplateNotificationContent(
            channel_registration_id=self.channel_id, to=[self.phone_number], template=sample_purchase_feedback
        )

        # calling send() with whatsapp message details
        message_responses = messaging_client.send(template_options)
        response = message_responses.receipts[0]
        print(
            "WhatsApp Call To Action Templated Message with message id {} was successfully sent to {}".format(
                response.message_id, response.to
            )
        )

    def send_template_message_with_location(self):

        from azure.communication.messages import NotificationMessagesClient
        from azure.communication.messages.models import (
            TemplateNotificationContent,
            MessageTemplate,
            MessageTemplateText,
            WhatsAppMessageTemplateBindings,
            WhatsAppMessageTemplateBindingsComponent,
            MessageTemplateLocation,
        )

        messaging_client = NotificationMessagesClient.from_connection_string(self.connection_string)

        # Setting template options
        templateName = "sample_movie_location"
        templateLanguage = "en_us"
        sample_movie_location: MessageTemplate = MessageTemplate(name=templateName, language=templateLanguage)
        name = MessageTemplateText(name="first", text="Joe")
        location = MessageTemplateLocation(
            name="location",
            location_name="Pablo Morales",
            address="1 Hacker Way, Menlo Park, CA 94025",
            latitude=37.483307,
            longitude=122.148981,
        )
        bindings = WhatsAppMessageTemplateBindings(
            body=[WhatsAppMessageTemplateBindingsComponent(ref_value=name.name)],
            header=[WhatsAppMessageTemplateBindingsComponent(ref_value=location.name)],
        )
        sample_movie_location.bindings = bindings
        sample_movie_location.template_values = [name, location]
        template_options = TemplateNotificationContent(
            channel_registration_id=self.channel_id, to=[self.phone_number], template=sample_movie_location
        )

        # calling send() with whatsapp message details
        message_responses = messaging_client.send(template_options)
        response = message_responses.receipts[0]
        print(
            "WhatsApp Location Templated Message with message id {} was successfully sent to {}".format(
                response.message_id, response.to
            )
        )


if __name__ == "__main__":
    sample = SendWhatsAppTemplateMessageSample()
    sample.send_template_send_message()
    sample.send_template_message_with_parameters()
    sample.send_template_message_with_buttons()
    sample.send_template_message_with_location()
    sample.send_template_message_with_call_to_action()
    sample.send_template_message_with_media()
