# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import json
import datetime
import logging


def fetch_current_datetime() -> str:
    """
    Get the current time as a JSON string.

    :return: The current time in JSON format.
    :rtype: str
    """
    current_time = datetime.datetime.now()
    time_json = json.dumps({"current_time": current_time.strftime("%Y-%m-%d %H:%M:%S")})
    return time_json


def fetch_weather(location: str) -> str:
    """
    Fetches the weather information for the specified location.

    :param location (str): The location to fetch weather for.
    :return: Weather information as a JSON string.
    :rtype: str
    """
    # In a real-world scenario, you'd integrate with a weather API.
    # Here, we'll mock the response.
    mock_weather_data = {
        "New York": "Sunny, 25°C",
        "London": "Cloudy, 18°C",
        "Tokyo": "Rainy, 22°C"
    }
    weather = mock_weather_data.get(location, "Weather data not available for this location.")
    weather_json = json.dumps({"weather": weather})
    return weather_json


def send_email(recipient: str, subject: str, body: str) -> str:
    """
    Sends an email with the specified subject and body to the recipient.

    :param recipient (str): Email address of the recipient.
    :param subject (str): Subject of the email.
    :param body (str): Body content of the email.
    :return: Confirmation message.
    :rtype: str
    """
    # In a real-world scenario, you'd use an SMTP server or an email service API.
    # Here, we'll mock the email sending.
    logging.info(f"Sending email to {recipient}...")
    logging.info(f"Subject: {subject}")
    logging.info(f"Body:\n{body}")

    message_json = json.dumps({"message": f"Email successfully sent to {recipient}."})
    return message_json


# Statically defined user functions for fast reference
user_functions = {"fetch_current_datetime": fetch_current_datetime, 
                  "fetch_weather": fetch_weather, 
                  "send_email": send_email
}
