from azure.ai.client import AzureAIClient
from azure.identity import DefaultAzureCredential
from azure.ai.client.models import AppInsightsConfiguration, EvaluatorConfiguration, SamplingStrategy, EvaluationSchedule, CronTrigger

def main():
    app_insights_config = AppInsightsConfiguration(
        resource_id="sample_id",
        query="your_connection_string",
        service_name="sample_service_name"
    )

    f1_evaluator_config = EvaluatorConfiguration(
        id="azureml://registries/jamahaja-evals-registry/models/F1ScoreEvaluator/versions/1"
    )

    custom_relevance_evaluator_config = EvaluatorConfiguration(
        id="azureml://registries/jamahaja-evals-registry/models/Relevance-Evaluator-AI-Evaluation/versions/2",
        init_params={"param3": "value3", "param4": "value4"},
        data_mapping={"data3": "value3", "data4": "value4"}
    )

    cron_expression = "0 0 0 1/1 * ? *"
    cron_trigger = CronTrigger(expression=cron_expression)
    evaluators = {
        "f1_score": f1_evaluator_config,
        "relevance": custom_relevance_evaluator_config
    }

    sampling_strategy = SamplingStrategy(rate=0.2)
    display_name = "Sample Online Evaluation Schedule"
    description = "Sample Online Evaluation Schedule Description"
    tags = {"tag1": "value1", "tag2": "value2"}
    properties = {"property1": "value1", "property2": "value2"}

    evaluation_schedule = EvaluationSchedule(
        data=app_insights_config,
        evaluators=evaluators,
        trigger=cron_trigger,
        sampling_strategy=sampling_strategy,
        display_name=display_name,
        description=description,
        tags=tags,
        properties=properties
    )

    # Project Configuration
    Subscription = "<subscription_id>"
    ResourceGroup = "<resource_group_name>"
    Workspace = "<workspace_name>"
    Endpoint = "<endpoint>"
    client = AzureAIClient.from_connection_string(
        credential=DefaultAzureCredential(),
        conn_str=f"{Endpoint};{Subscription};{ResourceGroup};{Workspace}",
        logging_enable=True
    )
    client.evaluations
    evaluation_schedule = client.evaluations.create_or_replace_schedule(id= "sample_schedule_id", resource=evaluation_schedule)
    client.evaluations.get_schedule(evaluation_schedule.id)
    client.evaluations.list_schedule()
    client.evaluations.list()
    client.evaluations.delete_schedule(evaluation_schedule.id)
    

if __name__ == "__main__":
    main()