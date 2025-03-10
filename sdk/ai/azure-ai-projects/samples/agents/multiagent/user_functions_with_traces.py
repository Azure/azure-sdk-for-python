# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import json
import datetime
from typing import Any, Callable, Set, Optional
from opentelemetry import trace


tracer = trace.get_tracer(__name__)


# These are the user-defined functions that can be called by the agent.
@tracer.start_as_current_span("fetch_current_datetime")  # type: ignore
def fetch_current_datetime(format: Optional[str] = None) -> str:
    """
    Get the current time as a JSON string, optionally formatted.

    :param format (Optional[str]): The format in which to return the current time. Defaults to None, which uses a standard format.
    :return: The current time in JSON format.
    :rtype: str
    """
    current_time = datetime.datetime.now()

    # Use the provided format if available, else use a default format
    if format:
        time_format = format
    else:
        time_format = "%Y-%m-%d %H:%M:%S"

    time_json = json.dumps({"current_time": current_time.strftime(time_format)})
    return time_json


@tracer.start_as_current_span("fetch_weather")  # type: ignore
def fetch_weather(location: str) -> str:
    """
    Fetches the weather information for the specified location.

    :param location (str): The location to fetch weather for.
    :return: Weather information as a JSON string.
    :rtype: str
    """
    # In a real-world scenario, you'd integrate with a weather API.
    # Here, we'll mock the response.
    mock_weather_data = {"New York": "Sunny, 25°C", "London": "Cloudy, 18°C", "Tokyo": "Rainy, 22°C"}
    weather = mock_weather_data.get(location, "Weather data not available for this location.")
    weather_json = json.dumps({"weather": weather})
    return weather_json


@tracer.start_as_current_span("send_email_using_recipient_name")  # type: ignore
def send_email_using_recipient_name(recipient: str, subject: str, body: str) -> str:
    """
    Sends an email with the specified subject and body to the recipient.

    :param recipient (str): Name of the recipient.
    :param subject (str): Subject of the email.
    :param body (str): Body content of the email.
    :return: Confirmation message.
    :rtype: str
    """
    # In a real-world scenario, you'd use an SMTP server or an email service API.
    # Here, we'll mock the email sending.
    print(f"Sending email to {recipient}...")
    print(f"Subject: {subject}")
    print(f"Body:\n{body}")

    message_json = json.dumps({"message": f"Email successfully sent to {recipient}."})
    return message_json


@tracer.start_as_current_span("convert_temperature")  # type: ignore
def convert_temperature(celsius: float) -> str:
    """Converts temperature from Celsius to Fahrenheit.

    :param celsius (float): Temperature in Celsius.
    :rtype: float

    :return: Temperature in Fahrenheit.
    :rtype: str
    """
    fahrenheit = (celsius * 9 / 5) + 32
    return json.dumps({"fahrenheit": fahrenheit})


# Example User Input for Each Function
# 1. Fetch Current DateTime
#    User Input: "What is the current date and time?"
#    User Input: "What is the current date and time in '%Y-%m-%d %H:%M:%S' format?"

# 2. Fetch Weather
#    User Input: "Can you provide the weather information for New York?"

# 3. Send Email Using Recipient Name
#    User Input: "Send an email to John Doe with the subject 'Meeting Reminder' and body 'Don't forget our meeting at 3 PM.'"

# 4. Convert Temperature
#    User Input: "Convert 25 degrees Celsius to Fahrenheit."


# Statically defined user functions for fast reference
user_functions: Set[Callable[..., Any]] = {
    fetch_current_datetime,
    fetch_weather,
    send_email_using_recipient_name,
    convert_temperature,
}
