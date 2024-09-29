import json
import datetime


def fetch_current_datetime():
    """
    Get the current time as a JSON string.

    :return: The current time in JSON format.
    :rtype: str
    """
    current_time = datetime.datetime.now()
    time_json = json.dumps({"current_time": current_time.strftime("%Y-%m-%d %H:%M:%S")})
    return time_json


# Statically defined user functions for fast reference
user_functions = {"fetch_current_datetime": fetch_current_datetime}
