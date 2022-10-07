# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: rank_actions_and_reward_events.py
DESCRIPTION:
    This sample demos sending a rank and reward call to personalizer
USAGE: python rank_actions_and_reward_events.py
Environment variables PERSONALIZER_ENDPOINT and PERSONALIZER_API_KEY must be set as per your personalizer instance.
"""
import os
import sys
from azure.ai.personalizer import PersonalizerClient
from azure.core.credentials import AzureKeyCredential


def main():
    client = get_personalizer_client()

    actions = [
        {
            "id": "Video1",
            "features": [
                {"videoType": "documentary", "videoLength": 35, "director": "CarlSagan"},
                {"mostWatchedByAge": "50-55"},
            ],
        },
        {
            "id": "Video2",
            "features": [
                {"videoType": "movie", "videoLength": 120, "director": "StevenSpielberg"},
                {"mostWatchedByAge": "40-45"},
            ],
        },
    ]
    context_features = [
        {"Features": {"day": "tuesday", "time": "night", "weather": "rainy"}},
        {
            "Features": {
                "payingUser": True,
                "favoriteGenre": "documentary",
                "hoursOnSite": 0.12,
                "lastWatchedType": "movie",
            },
        },
    ]

    request = {
        "actions": actions,
        "contextFeatures": context_features,
    }

    print("Sending rank request")
    rank_response = client.rank(request)
    print("Rank returned response with event id {} and recommended {} as the best action"
          .format(rank_response.get("eventId"), rank_response.get("rewardActionId")))

    # The event response will be determined by how the user interacted with the action that was presented to them.
    # Let us say that they like the action. So we associate a reward of 1.
    print("Sending reward event")
    client.events.reward(rank_response.get("eventId"), {"value": 1.0})
    print("Completed sending reward response")


def get_personalizer_client():
    endpoint = get_endpoint()
    api_key = get_api_key()
    return PersonalizerClient(endpoint, AzureKeyCredential(api_key))


def get_endpoint():
    try:
        return os.environ['PERSONALIZER_ENDPOINT']
    except KeyError:
        print("PERSONALIZER_ENDPOINT must be set.")
        sys.exit(1)


def get_api_key():
    try:
        return os.environ['PERSONALIZER_API_KEY']
    except KeyError:
        print("PERSONALIZER_API_KEY must be set.")
        sys.exit(1)


if __name__ == "__main__":
    main()
