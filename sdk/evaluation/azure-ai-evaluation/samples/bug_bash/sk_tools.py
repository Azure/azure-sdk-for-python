import json
import datetime
from typing import Any, Dict, List, Optional, Annotated
from semantic_kernel.functions import kernel_function


class AgentToolsPlugin:
    """
    Plugin containing utility functions for time, weather, email, math, and more.
    """

    @kernel_function(
        description="Get the current time as a JSON string, optionally formatted."
    )
    def fetch_current_datetime(
        self,
        format: Annotated[
            Optional[str], "Optional time format string, e.g., '%Y-%m-%d %H:%M:%S'"
        ] = None,
    ) -> Annotated[str, "The current time in JSON format."]:
        """
        Get the current time as a JSON string, optionally formatted.
        """
        current_time = datetime.datetime.now()
        time_format = format if format else "%Y-%m-%d %H:%M:%S"
        time_json = json.dumps({"current_time": current_time.strftime(time_format)})
        return time_json

    @kernel_function(
        description="Fetches the weather information for the specified location."
    )
    def fetch_weather(
        self, location: Annotated[str, "The location to fetch weather for."]
    ) -> Annotated[str, "Weather information as a JSON string."]:
        """
        Fetches the weather information for the specified location.
        """
        mock_weather_data = {
            "New York": "Sunny, 25°C",
            "London": "Cloudy, 18°C",
            "Tokyo": "Rainy, 22°C",
        }
        weather = mock_weather_data.get(
            location, "Weather data not available for this location."
        )
        return json.dumps({"weather": weather})

    @kernel_function(
        description="Sends an email with the specified subject and body to the recipient email address."
    )
    def send_email(
        self,
        recipient: Annotated[str, "Email address of the recipient."],
        subject: Annotated[str, "Subject of the email."],
        body: Annotated[str, "Body content of the email."],
    ) -> Annotated[str, "Confirmation message as JSON."]:
        """
        Sends an email with the specified subject and body to the recipient.
        """
        return json.dumps({"message": f"Email successfully sent to {recipient}."})

    @kernel_function(description="Sends an email to a recipient specified by name.")
    def send_email_using_recipient_name(
        self,
        recipient: Annotated[str, "Name of the recipient."],
        subject: Annotated[str, "Subject of the email."],
        body: Annotated[str, "Body content of the email."],
    ) -> Annotated[str, "Confirmation message as JSON."]:
        """
        Sends an email with the specified subject and body to the recipient.
        """
        return json.dumps({"message": f"Email successfully sent to {recipient}."})

    @kernel_function(description="Calculates the sum of two integers.")
    def calculate_sum(
        self, a: Annotated[int, "First integer."], b: Annotated[int, "Second integer."]
    ) -> Annotated[str, "The sum of the two integers as a JSON string."]:
        """
        Calculates the sum of two integers.
        """
        result = a + b
        return json.dumps({"result": result})

    @kernel_function(description="Converts temperature from Celsius to Fahrenheit.")
    def convert_temperature(
        self, celsius: Annotated[float, "Temperature in Celsius."]
    ) -> Annotated[str, "Temperature in Fahrenheit as a JSON string."]:
        """
        Converts temperature from Celsius to Fahrenheit.
        """
        fahrenheit = (celsius * 9 / 5) + 32
        return json.dumps({"fahrenheit": fahrenheit})

    @kernel_function(description="Toggles a boolean flag.")
    def toggle_flag(
        self, flag: Annotated[bool, "The flag to toggle."]
    ) -> Annotated[str, "The toggled flag as a JSON string."]:
        """
        Toggles a boolean flag.
        """
        toggled = not flag
        return json.dumps({"toggled_flag": toggled})

    @kernel_function(description="Merges two dictionaries.")
    def merge_dicts(
        self,
        dict1: Annotated[Dict[str, Any], "First dictionary."],
        dict2: Annotated[Dict[str, Any], "Second dictionary."],
    ) -> Annotated[str, "The merged dictionary as a JSON string."]:
        """
        Merges two dictionaries.
        """
        merged = dict1.copy()
        merged.update(dict2)
        return json.dumps({"merged_dict": merged})

    @kernel_function(description="Retrieves user information based on user ID.")
    def get_user_info(
        self, user_id: Annotated[int, "ID of the user."]
    ) -> Annotated[str, "User information as a JSON string."]:
        """
        Retrieves user information based on user ID.
        """
        mock_users = {
            1: {"name": "Alice", "email": "alice@example.com"},
            2: {"name": "Bob", "email": "bob@example.com"},
            3: {"name": "Charlie", "email": "charlie@example.com"},
        }
        user_info = mock_users.get(user_id, {"error": "User not found."})
        return json.dumps({"user_info": user_info})

    @kernel_function(description="Finds the longest word in each sentence.")
    def longest_word_in_sentences(
        self, sentences: Annotated[List[str], "A list of sentences."]
    ) -> Annotated[str, "A JSON string mapping each sentence to its longest word."]:
        """
        Finds the longest word in each sentence.
        """
        if not sentences:
            return json.dumps({"error": "The list of sentences is empty"})

        longest_words = {}
        for sentence in sentences:
            words = sentence.split()
            longest_word = max(words, key=len) if words else ""
            longest_words[sentence] = longest_word

        return json.dumps({"longest_words": longest_words})

    @kernel_function(
        description="Processes a list of records by summing integer values in each."
    )
    def process_records(
        self,
        records: Annotated[
            List[Dict[str, int]], "A list of dictionaries mapping strings to integers."
        ],
    ) -> Annotated[str, "A list of sums of the integer values in each record as JSON."]:
        """
        Process a list of records, where each record is a dictionary with string keys and integer values.
        """
        sums = [sum(record.values()) for record in records]
        return json.dumps({"sums": sums})
