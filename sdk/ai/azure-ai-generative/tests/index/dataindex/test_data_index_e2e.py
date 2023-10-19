import io
import logging
from contextlib import redirect_stdout

from azure.ai.ml import MLClient, load_data
from azure.ai.ml.dsl import pipeline
from azure.ai.generative.index._dataindex.data_index import index_data
from azure.ai.generative.index._dataindex.entities import CitationRegex, Data, DataIndex, Embedding, IndexSource, IndexStore

logger = logging.getLogger(__name__)


def wait_for_job(ml_client, job, stream_run_output=False):
    if stream_run_output:
        ml_client.jobs.stream(job.name)
    else:
        logger.info("Redirecting stdout while streaming Job output.")
        # TODO: Write to file?
        job_output = io.StringIO()
        with redirect_stdout(job_output):
            ml_client.jobs.stream(job.name)
        logger.info("Job finished streaming.")


def test_cog_search_docs_faiss_dataindex(ml_client, aoai_connection, experiment_name, stream_run_output):
    # Create DataIndex configuration
    asset_name = "azure_search_docs_aoai_faiss"

    data_index = DataIndex(
        name=asset_name,
        description="Azure Cognitive Search docs embedded with text-embedding-ada-002 and indexed in a Faiss Index.",
        source=IndexSource(
            input_data=Data(
                type="uri_folder",
                path="<This will be replaced later>",
            ),
            input_glob="articles/search/**/*",
            citation_url="https://learn.microsoft.com/en-us/azure",
            # Remove articles from the final citation url and remove the file extension so url points to hosted docs, not GitHub.
            citation_url_replacement_regex=CitationRegex(
                match_pattern="(.*)/articles/(.*)(\\.[^.]+)$",
                replacement_pattern="\\1/\\2"
            )
        ),
        embedding=Embedding(
            model="text-embedding-ada-002",
            connection=aoai_connection,
            cache_path=f"azureml://datastores/workspaceblobstore/paths/embeddings_cache/{asset_name}",
        ),
        index=IndexStore(
            type="faiss"
        ),
        # name is replaced with a unique value each time the job is run
        path=f"azureml://datastores/workspaceblobstore/paths/indexes/{asset_name}/{{name}}"
    )

    # Use git_clone Component to clone Azure Search docs from github
    ml_registry = MLClient(credential=ml_client._credential, registry_name="azureml")

    git_clone_component = ml_registry.components.get("llm_rag_git_clone", label="latest")

    # Clone Git Repo and use as input to index_job
    @pipeline(default_compute="serverless")
    def git_to_faiss(
        git_url,
        branch_name="",
        git_connection_id="",
    ):
        git_clone = git_clone_component(
            git_repository=git_url,
            branch_name=branch_name
        )
        git_clone.environment_variables["AZUREML_WORKSPACE_CONNECTION_ID_GIT"] = git_connection_id

        index_job = index_data(
            description=data_index.description,
            data_index=data_index,
            input_data_override=git_clone.outputs.output_data,
            ml_client=ml_client,
        )

        return index_job.outputs

    #
    git_index_job = git_to_faiss("https://github.com/MicrosoftDocs/azure-docs.git")
    # Ensure repo cloned each run to get latest, comment out to have first clone reused.
    git_index_job.settings.force_rerun = True

    # Submit the DataIndex Job
    git_index_run = ml_client.jobs.create_or_update(
        git_index_job,
        experiment_name=experiment_name,
    )

    # Wait for it to finish
    wait_for_job(ml_client, git_index_run, stream_run_output)

    # Check the created asset, it is a folder on storage containing an MLIndex yaml file
    mlindex_docs_index_asset = ml_client.data.get(asset_name, label="latest")

    # Try it out with langchain by loading the MLIndex asset using the azure-ai-generative SDK
    from azure.ai.generative.index import MLIndex

    mlindex = MLIndex(mlindex_docs_index_asset)

    index = mlindex.as_langchain_vectorstore()
    docs = index.similarity_search("How can I enable Semantic Search on my Index?", k=5)

    # Take a look at those chunked docs
    import json

    for doc in docs:
        logger.info(json.dumps({"content": doc.page_content, **doc.metadata}, indent=2))


def test_local_file_to_acs_dataindex(test_dir, test_data_dir, ai_client, ml_client, aoai_connection, acs_connection, acs_temp_index, experiment_name, stream_run_output):
    asset_name = "dataindex_test_documents_aoai_acs"
    data_index = DataIndex(
        name=asset_name,
        description="Azure Cognitive Search docs embedded with text-embedding-ada-002 and indexed in Azure Cognitive Search.",
        source=IndexSource(
            input_data=Data(
                type="uri_folder",
                path=test_data_dir / "documents" / "incremental_many_docs" / "first_run"
            ),
            chunk_size=500,
            citation_url="https://dev.azure.com/msdata/Vienna/_git/sdk-cli-v2?path=/src/azure-ai-generative/tests/data/documents/incremental_many_docs/first_run",
        ),
        embedding=Embedding(
            # TODO: Have aoai deployment (per-model kind) be listed from resource or passed in by test runner.
            model="azure_open_ai://deployment/text-embedding-ada-002/model/text-embedding-ada-002",
            connection=aoai_connection,
            cache_path=f"azureml://datastores/workspaceblobstore/paths/embeddings_cache/{asset_name}",
        ),
        index=IndexStore(
            type="acs",
            connection=acs_connection,
            name=acs_temp_index
        ),
        # name is replaced with a unique value each time the job is run
        path=f"azureml://datastores/workspaceblobstore/paths/indexes/{asset_name}/{{name}}"
    )

    # Submit the DataIndex Job
    index_job = ml_client.data.index_data(data_index=data_index, experiment_name=experiment_name)

    # Wait for it to finish
    wait_for_job(ml_client, index_job, stream_run_output)

    # Check the created asset, it is a folder on storage containing an MLIndex yaml file
    mlindex_docs_index_asset = ml_client.data.get(data_index.name, label="latest")

    # Try it out with langchain by loading the MLIndex asset using the azure-ai-generative SDK
    from azure.ai.generative.index import MLIndex

    mlindex = MLIndex(mlindex_docs_index_asset)

    # total_num_docs = mlindex.as_native_index_client().get_document_count()
    # logger.info(f"Index {mlindex.name} has {total_num_docs} docs.")
    index = mlindex.as_langchain_vectorstore()

    docs = index.similarity_search("What is an MLIndex?", k=5)

    # Take a look at those chunked docs
    import json

    for doc in docs:
        logger.info(json.dumps({"content": doc.page_content, **doc.metadata}, indent=2))


def test_s3_to_acs_dataindex(ml_client, aoai_connection, acs_connection, acs_temp_index, experiment_name, stream_run_output):
    asset_name = "s3_aoai_acs"

    data_index = DataIndex(
        name=asset_name,
        description="S3 data embedded with text-embedding-ada-002 and indexed in Azure Cognitive Search.",
        source=IndexSource(
            input_data=Data(
                type="uri_folder",
                path="abfss://9aa7b19e-c117-4a74-8654-cf1559ba9f4f@msit-onelake.dfs.fabric.microsoft.com/1606ee55-ec68-4658-8d6b-58bf8dd26636/Files/lupickup-test-s3",
            ),
            citation_url="s3://lupickup-test",
        ),
        embedding=Embedding(
            model="text-embedding-ada-002",
            connection=aoai_connection,
            cache_path=f"azureml://datastores/workspaceblobstore/paths/embeddings_cache/{asset_name}",
        ),
        index=IndexStore(
            type="acs",
            connection=acs_connection,
            name=acs_temp_index
        ),
        # name is replaced with a unique value each time the job is run
        path=f"azureml://datastores/workspaceblobstore/paths/indexes/{asset_name}/{{name}}"
    )

    # Create the DataIndex Job to be scheduled
    from azure.ai.ml import UserIdentityConfiguration

    index_job = ml_client.data.index_data(
        data_index=data_index,
        experiment_name=experiment_name,
        # The DataIndex Job will use the identity of the MLClient within the DataIndex Job to access source data.
        identity=UserIdentityConfiguration(),
    )

    # Wait for it to finish
    wait_for_job(ml_client, index_job, stream_run_output)

    # Check the created asset, it is a folder on storage containing an MLIndex yaml file
    mlindex_docs_index_asset = ml_client.data.get(data_index.name, label="latest")

    # Try it out with langchain by loading the MLIndex asset using the azure-ai-generative SDK
    from azure.ai.generative.index import MLIndex

    mlindex = MLIndex(mlindex_docs_index_asset)

    # total_num_docs = mlindex.as_native_index_client().get_document_count()
    # logger.info(f"Index {mlindex.name} has {total_num_docs} docs.")
    index = mlindex.as_langchain_vectorstore()

    docs = index.similarity_search("What is RAG?", k=5)

    # Take a look at those chunked docs
    import json

    for doc in docs:
        print(json.dumps({"content": doc.page_content, **doc.metadata}, indent=2))


def test_scheduled_s3_to_acs_dataindex(ml_client, aoai_connection, acs_connection, acs_temp_index, experiment_name):
    asset_name = "s3_aoai_acs"

    data_index = DataIndex(
        name=asset_name,
        description="S3 data embedded with text-embedding-ada-002 and indexed in Azure Cognitive Search.",
        source=IndexSource(
            input_data=Data(
                type="uri_folder",
                path="abfss://9aa7b19e-c117-4a74-8654-cf1559ba9f4f@msit-onelake.dfs.fabric.microsoft.com/1606ee55-ec68-4658-8d6b-58bf8dd26636/Files/lupickup-test-s3",
            ),
            citation_url="s3://lupickup-test",
        ),
        embedding=Embedding(
            model="text-embedding-ada-002",
            connection=aoai_connection,
            cache_path=f"azureml://datastores/workspaceblobstore/paths/embeddings_cache/{asset_name}",
        ),
        index=IndexStore(
            type="acs",
            connection=acs_connection,
            name=acs_temp_index
        ),
        # name is replaced with a unique value each time the job is run
        path=f"azureml://datastores/workspaceblobstore/paths/indexes/{asset_name}/{{name}}"
    )

    # Create the DataIndex Job to be scheduled
    from azure.ai.ml import UserIdentityConfiguration

    index_job = ml_client.data.index_data(
        data_index=data_index,
        experiment_name=experiment_name,
        # The DataIndex Job will use the identity of the MLClient within the DataIndex Job to access source data.
        identity=UserIdentityConfiguration(),
        # Instead of submitting the Job and returning the Run a PipelineJob configuration is returned which can be used in with a Schedule.
        submit_job=False
    )

    # Create Schedule for DataIndex Job
    from datetime import datetime, timedelta

    from azure.ai.ml.constants import TimeZone
    from azure.ai.ml.entities import JobSchedule, RecurrenceTrigger

    schedule_name = "onelake_s3_aoai_acs_mlindex_daily"

    schedule_start_time = datetime.utcnow() + timedelta(minutes=1)
    recurrence_trigger = RecurrenceTrigger(
        frequency="day",
        interval=1,
        #schedule=RecurrencePattern(hours=16, minutes=[15]),
        start_time=schedule_start_time,
        time_zone=TimeZone.UTC,
    )

    job_schedule = JobSchedule(
        name=schedule_name, trigger=recurrence_trigger, create_job=index_job, properties=index_job.properties
    )

    # Enable Schedule
    job_schedule_res = ml_client.schedules.begin_create_or_update(
        schedule=job_schedule
    ).result()
    logger.info(f"Updated Schedule Result: {job_schedule_res}")
    # Take a look at the schedule in Workspace Portal
    logger.info(f"Schedule Link: https://ml.azure.com/schedule/{schedule_name}/details/overview?wsid=/subscriptions/{ml_client.subscription_id}/resourceGroups/{ml_client.resource_group_name}/providers/Microsoft.MachineLearningServices/workspaces/{ml_client.workspace_name}")

    # Get the MLIndex Asset
    onelake_s3_index_asset = ml_client.data.get(asset_name, label="latest")

    # Try it out with langchain by loading the MLIndex asset using the azure-ai-generative SDK
    from azure.ai.generative.index import MLIndex

    mlindex = MLIndex(onelake_s3_index_asset)

    # total_num_docs = mlindex.as_native_index_client().get_document_count()
    # logger.info(f"Index {mlindex.name} has {total_num_docs} docs.")
    index = mlindex.as_langchain_vectorstore()

    docs = index.similarity_search("What is RAG?", k=5)

    # Take a look at those chunked docs
    import json

    for doc in docs:
        print(json.dumps({"content": doc.page_content, **doc.metadata}, indent=2))

