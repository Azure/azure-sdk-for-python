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
"""
import asyncio

from util import get_async_personalizer_client


async def main():
    client = get_async_personalizer_client()

    # We want to rank the actions for two slots.
    slots = [
        {
            "id": "Main Article",
            "baselineAction": "NewsArticle",
            "features": [{"Size": "Large", "Position": "Top Middle"}],
        },
        {
            "id": "Side Bar",
            "baselineAction": "SportsArticle",
            "features": [{"Size": "Small", "Position": "Bottom Right"}],
        },
    ]

    # The list of actions to be ranked with metadata associated for each action.
    actions = [
        {"id": "NewsArticle", "features": [{"type": "News"}]},
        {"id": "SportsArticle", "features": [{"type": "Sports"}]},
        {"id": "EntertainmentArticle", "features": [{"type": "Entertainment"}]},
    ]

    context_features = [
        {"User": {"ProfileType": "AnonymousUser", "LatLong": "47.6,-122.1"}},
        {"Environment": {"DayOfMonth": "28", "MonthOfYear": "8", "Weather": "Sunny"}},
        {"Device": {"Mobile": True, "Windows": True}},
        {"RecentActivity": {"ItemsInCart": 3}},
    ]

    request = {
        "slots": slots,
        "actions": actions,
        "contextFeatures": context_features
    }
    print("Sending multi-slot rank request")
    rank_response = await client.multi_slot.rank(request)
    print("Rank returned response with event id {} and recommended the following:"
          .format(rank_response.get("eventId")))
    for slot in rank_response.get("slots"):
        print("Action: {} for slot: {}".format(slot.get("rewardActionId"), slot.get("id")))

    # The event response will be determined by how the user interacted with the action that was presented to them.
    # Let us say that they like the action presented to them for the Main Article slot. So we associate a reward of 1.
    print("Sending reward event for Main Article slot")
    await client.multi_slot_events.reward(
        rank_response.get("eventId"),
        {"reward": [{"slotId": "Main Article", "value": 1.0}]})
    print("Completed sending reward response")


if __name__ == "__main__":
    asyncio.run(main())
