from azure.ai.projects import AIProjectClient

from azure.identity import DefaultAzureCredential
from azure.ai.projects.models import (
    ApplicationInsightsConfiguration,
    EvaluatorConfiguration,
    EvaluationSchedule,
    CronTrigger,
    RecurrenceTrigger,
    Frequency,
    RecurrenceSchedule,
)


def main():
    # Project Configuration Canary
    Subscription = "<subscription_id>"
    ResourceGroup = "<resource_group>"
    Workspace = "<workspace>>"
    Endpoint = "<endpoint>"

    # Create an Azure AI client
    ai_client = AIProjectClient.from_connection_string(
        credential=DefaultAzureCredential(),
        conn_str=f"{Endpoint};{Subscription};{ResourceGroup};{Workspace}",
        logging_enable=True,  # Optional. Remove this line if you don't want to show how to enable logging
    )

    # Sample for creating an evaluation schedule with recurrence trigger of daily frequency

    app_insights_config = ApplicationInsightsConfiguration(
        resource_id="<resource_id>",
        query='traces | where message contains ""',
        service_name="sample_service_name",
    )

    f1_evaluator_config = EvaluatorConfiguration(
        id="azureml://registries/model-evaluation-dev-01/models/F1ScoreEval/versions/1",
        init_params={
            "column_mapping": {
                "response": "${data.message}",
                "ground_truth": "${data.itemType}",
            }
        },
    )

    recurrence_trigger = RecurrenceTrigger(frequency="daily", interval=1)
    evaluators = {
        "f1_score": f1_evaluator_config,
    }

    name = "CANARY-ONLINE-EVAL-TEST-WS-ENV-104"
    description = "Testing Online eval command job in CANARY environment"
    tags = {"tag1": "value1", "tag2": "value2"}

    evaluation_schedule = EvaluationSchedule(
        data=app_insights_config,
        evaluators=evaluators,
        trigger=recurrence_trigger,
        description=description,
        tags=tags,
    )

    evaluation_schedule = ai_client.evaluations.create_or_replace_schedule(name, evaluation_schedule)
    print(evaluation_schedule.provisioning_state)
    print(evaluation_schedule)

    # Sample for get an evaluation schedule with name
    evaluation_schedule = ai_client.evaluations.get_schedule(name)
    print(evaluation_schedule)

    # Sample for list evaluation schedules
    for evaluation_schedule in ai_client.evaluations.list_schedule():
        print(evaluation_schedule)

    # Sample for disable an evaluation schedule with name
    ai_client.evaluations.disable_schedule(name)


if __name__ == "__main__":
    main()
