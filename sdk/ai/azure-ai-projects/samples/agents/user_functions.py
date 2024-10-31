# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import json
import datetime
from typing import Any, Callable, Set, Dict, List

# These are the user-defined functions that can be called by the agent.


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
    mock_weather_data = {"New York": "Sunny, 25°C", "London": "Cloudy, 18°C", "Tokyo": "Rainy, 22°C"}
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
    print(f"Sending email to {recipient}...")
    print(f"Subject: {subject}")
    print(f"Body:\n{body}")

    message_json = json.dumps({"message": f"Email successfully sent to {recipient}."})
    return message_json


def calculate_sum(a: int, b: int) -> str:
    """Calculates the sum of two integers.
    
    :param a (int): First integer.
    :rtype: int
    :param b (int): Second integer.
    :rtype: int

    :return: The sum of the two integers.
    :rtype: str
    """
    result = a + b
    return json.dumps({"result": result})


def convert_temperature(celsius: float) -> str:
    """Converts temperature from Celsius to Fahrenheit.
    
    :param celsius (float): Temperature in Celsius.
    :rtype: float

    :return: Temperature in Fahrenheit.
    :rtype: str
    """
    fahrenheit = (celsius * 9/5) + 32
    return json.dumps({"fahrenheit": fahrenheit})


def toggle_flag(flag: bool) -> str:
    """Toggles a boolean flag.
    
    :param flag (bool): The flag to toggle.
    :rtype: bool

    :return: The toggled flag.
    :rtype: str
    """
    toggled = not flag
    return json.dumps({"toggled_flag": toggled})


def merge_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> str:
    """Merges two dictionaries.
    
    :param dict1 (Dict[str, Any]): First dictionary.
    :rtype: dict
    :param dict2 (Dict[str, Any]): Second dictionary.
    :rtype: dict

    :return: The merged dictionary.
    :rtype: str
    """
    merged = dict1.copy()
    merged.update(dict2)
    return json.dumps({"merged_dict": merged})


def get_user_info(user_id: int) -> str:
    """Retrieves user information based on user ID.
    
    :param user_id (int): ID of the user.
    :rtype: int

    :return: User information as a JSON string.
    :rtype: str
    """
    mock_users = {
        1: {"name": "Alice", "email": "alice@example.com"},
        2: {"name": "Bob", "email": "bob@example.com"},
        3: {"name": "Charlie", "email": "charlie@example.com"},
    }
    user_info = mock_users.get(user_id, {"error": "User not found."})
    return json.dumps({"user_info": user_info})


def longest_word_in_sentences(sentences: List[str]) -> str:
    """Finds the longest word in each sentence.
    
    :param sentences (List[str]): A list of sentences.
    :return: A JSON string mapping each sentence to its longest word.
    :rtype: str
    """
    if not sentences:
        return json.dumps({"error": "The list of sentences is empty"})

    longest_words = {}
    for sentence in sentences:
        # Split sentence into words
        words = sentence.split()
        if words:
            # Find the longest word
            longest_word = max(words, key=len)
            longest_words[sentence] = longest_word
        else:
            longest_words[sentence] = ""

    return json.dumps({"longest_words": longest_words})


# Example Questions for Each Function
# 1. Fetch Current DateTime
#    Question: "What is the current date and time?"

# 2. Fetch Weather
#    Question: "Can you provide the weather information for New York?"

# 3. Send Email
#    Question: "Send an email to john.doe@example.com with the subject 'Meeting Reminder' and body 'Don't forget our meeting at 3 PM.'"

# 4. Calculate Sum
#    Question: "What is the sum of 45 and 55?"

# 5. Convert Temperature
#    Question: "Convert 25 degrees Celsius to Fahrenheit."

# 6. Toggle Flag
#    Question: "Toggle the flag True."

# 7. Merge Dictionaries
#    Question: "Merge these two dictionaries: {'name': 'Alice'} and {'age': 30}."

# 8. Get User Info
#    Question: "Retrieve user information for user ID 1."

# 9. Longest Word in Sentences
#    Question: "Find the longest word in each of these sentences: ['The quick brown fox jumps over the lazy dog', 'Python is an amazing programming language', 'Azure AI capabilities are impressive']."

# Statically defined user functions for fast reference
user_functions: Set[Callable[..., Any]] = {
    fetch_current_datetime,
    fetch_weather,
    send_email,
    calculate_sum,
    convert_temperature,
    toggle_flag,
    merge_dicts,
    get_user_info,
    longest_word_in_sentences,
}
