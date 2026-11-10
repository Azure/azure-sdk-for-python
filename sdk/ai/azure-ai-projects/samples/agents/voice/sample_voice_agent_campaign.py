# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Create a future-scheduled outbound campaign (preview), wait for preparation,
    then cancel and delete it. Campaign LROs use the SDK's built-in polling:
    create/cancel return a campaign through an operation-guarded final GET;
    delete completes without fetching the deleted campaign.

    Requires an existing voice agent and a project telephony connection that
    supports outbound calls from the source phone number. Use a destination
    you own or have permission to call. Creation authorizes dialing: if the
    sample is interrupted before cancellation, calls may start tomorrow.
    Preparation completion does not mean all calls have finished.

USAGE:
    python sample_voice_agent_campaign.py

    pip install "azure-ai-projects>=2.11.0" azure-identity python-dotenv

    Environment variables:
    1) FOUNDRY_PROJECT_ENDPOINT (required) - The Foundry project endpoint.
    2) FOUNDRY_VOICE_AGENT_NAME (optional) - Defaults to "MyVoiceAgent".
    3) FOUNDRY_VOICE_CONNECTION_NAME (optional) - Defaults to "MyTelephonyConnection".
    4) FOUNDRY_VOICE_SOURCE_PHONE_NUMBER (optional) - Defaults to "+15555550100".
    5) FOUNDRY_VOICE_DESTINATION_PHONE_NUMBER (optional) - Defaults to "+15555550101".

    Edit the sample defaults below or override them through environment variables.
    Replace the illustrative connection and phone numbers with your own values.
"""

import os
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from dotenv import load_dotenv

from azure.core import MatchConditions
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    AtTimeSchedule,
    PhoneNumber,
    TelephonyCampaign,
    TelephonyRecipient,
)


def main() -> None:
    load_dotenv()
    endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
    agent_name = os.environ.get("FOUNDRY_VOICE_AGENT_NAME", "MyVoiceAgent")
    campaign_name = f"sample-campaign-{uuid4().hex}"
    scheduled_at = datetime.now(timezone.utc) + timedelta(days=1)
    campaign = TelephonyCampaign(
        connection_name=os.environ.get(
            "FOUNDRY_VOICE_CONNECTION_NAME", "MyTelephonyConnection"
        ),
        source=PhoneNumber(
            value=os.environ.get("FOUNDRY_VOICE_SOURCE_PHONE_NUMBER", "+15555550100")
        ),
        recipients=[
            TelephonyRecipient(
                destination=PhoneNumber(
                    value=os.environ.get(
                        "FOUNDRY_VOICE_DESTINATION_PHONE_NUMBER", "+15555550101"
                    )
                )
            )
        ],
        schedule=AtTimeSchedule(
            scheduled_at=scheduled_at, expires_at=scheduled_at + timedelta(hours=1)
        ),
    )

    with (
        DefaultAzureCredential() as credential,
        AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
    ):
        campaigns = project_client.beta.voice_agents.telephony
        create_poller = None
        try:
            create_poller = campaigns.begin_create(
                agent_name=agent_name,
                campaign_name=campaign_name,
                campaign=campaign,
            )
            print(
                f"Preparing campaign '{campaign_name}'. Calls are scheduled for {scheduled_at.isoformat()}."
            )
            prepared = create_poller.result()
            print(f"Preparation finished: campaign status={prepared.status}")
        finally:
            if create_poller is not None:
                # Read a fresh ETag before each conditional control action.
                current = campaigns.get(
                    agent_name=agent_name, campaign_name=campaign_name
                )
                if current.status in {"validating", "running"}:
                    cancel_poller = campaigns.begin_cancel(
                        agent_name=agent_name,
                        campaign_name=campaign_name,
                        etag=current.etag,
                        match_condition=MatchConditions.IfNotModified,
                    )
                    cancelled = cancel_poller.result()
                    print(f"Cancellation finished: campaign status={cancelled.status}")

                current = campaigns.get(
                    agent_name=agent_name, campaign_name=campaign_name
                )
                delete_poller = campaigns.begin_delete(
                    agent_name=agent_name,
                    campaign_name=campaign_name,
                    etag=current.etag,
                    match_condition=MatchConditions.IfNotModified,
                )
                delete_poller.result()
                print(
                    f"Deleted sample campaign '{campaign_name}'. The agent and connection were preserved."
                )


if __name__ == "__main__":
    main()
