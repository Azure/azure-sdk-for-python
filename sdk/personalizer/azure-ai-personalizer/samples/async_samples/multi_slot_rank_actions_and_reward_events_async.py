# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: multi_slot_rank_actions_and_reward_events_async.py
DESCRIPTION:
    This sample demos sending a rank and reward call to personalizer for multi-slot configuration.
USAGE: python multi_slot_rank_actions_and_reward_events_async.py
Environment variables PERSONALIZER_ENDPOINT and PERSONALIZER_API_KEY must be set as per your personalizer instance.
"""
import asyncio
import os
import sys
from azure.ai.personalizer.aio import PersonalizerClient
from azure.core.credentials import AzureKeyCredential


async def main():
    try:
        endpoint = os.environ['PERSONALIZER_ENDPOINT_MULTI_SLOT']
    except KeyError:
        print("PERSONALIZER_ENDPOINT_MULTI_SLOT must be set.")
        sys.exit(1)

    try:
        api_key = os.environ['PERSONALIZER_API_KEY_MULTI_SLOT']
    except KeyError:
        print("PERSONALIZER_API_KEY_MULTI_SLOT must be set.")
        sys.exit(1)

    client = PersonalizerClient(endpoint, AzureKeyCredential(api_key))

    # We want to rank the actions for two slots.
    slots = [
        {
            "id": "Main Article",
            "baselineAction": "NewsArticle",
            "positionFeatures": [{"Size": "Large", "Position": "Top Middle"}],
        },
        {
            "id": "Side Bar",
            "baselineAction": "SportsArticle",
            "positionFeatures": [{"Size": "Small", "Position": "Bottom Right"}],
        },
    ]

    # The list of actions to be ranked with metadata associated for each action.
    actions = [
        {"id": "NewsArticle", "features": [{"type": "News"}]},
        {"id": "SportsArticle", "features": [{"type": "Sports"}]},
        {"id": "EntertainmentArticle", "features": [{"type": "Entertainment"}]},
    ]

    # Context of the user to which the action must be presented.
    context_features = [
        {"user": {"profileType": "AnonymousUser", "latLong": "47.6,-122.1"}},
        {"environment": {"dayOfMonth": "28", "monthOfYear": "8", "weather": "Sunny"}},
        {"device": {"mobile": True, "windows": True}},
        {"recentActivity": {"itemsInCart": 3}},
    ]

    request = {
        "slots": slots,
        "actions": actions,
        "contextFeatures": context_features
    }

    print("Sending multi-slot rank request")
    rank_response = await client.rank_multi_slot(request)
    print("Rank returned response with event id {} and recommended the following:"
          .format(rank_response.get("eventId")))
    for slot in rank_response.get("slots"):
        print("Action: {} for slot: {}".format(slot.get("rewardActionId"), slot.get("id")))

    # The event response will be determined by how the user interacted with the action that was presented to them.
    # Let us say that they like the action presented to them for Main Article slot. So we associate a reward of 1.
    print("Sending reward event for Main Article slot")
    await client.reward_multi_slot(
        rank_response.get("eventId"),
        {"reward": [{"slotId": "Main Article", "value": 1.0}]})
    print("Completed sending reward response")


if __name__ == "__main__":
    asyncio.run(main())
