import logging
import uuid
from datetime import datetime
from pathlib import Path

import pytest
from azure.core.exceptions import ResourceNotFoundError
from azure.ai.generative.entities import Connection

logger = logging.getLogger(__name__)


def index_pytest_addoption(parser):
    # TODO: Run `az ad signed-in-user show`, parse as json, use `userPrincipalName` via r'(.*)@microsoft.com' as alias.
    parser.addoption("--experiment-name", default=f"dev-index-e2e-{datetime.utcnow().month:02}{datetime.utcnow().day:02}",
                     help="Name of experiment to run all tests under, defaults to index-e2e-<month><day>.")
    parser.addoption("--stream-run-output", action="store_true", default=False)
    # Where to load Index components from.
    parser.addoption("--component-source", default="dev", help="Local dev components are used by default, use 'registry:<registry_name>' to use components from a registry.")
    # Resource Connections needed by Index tests
    parser.addoption("--aoai-connection-name", default="aoai_connection")
    parser.addoption("--document-intelligence-connection-name", default="document_intelligence")
    parser.addoption("--acs-connection-name", default="acs_connection")
    parser.addoption("--keep-acs-index", action="store_true", default=False)
    parser.addoption("--acs-index-name", default=None)


def pytest_generate_tests():
    return ["experiment_name", "stream_run_output",
            "component_source", "aoai_connection_name", "document_intelligence_connection_name",
            "acs_connection_name", "keep_acs_index", "acs_index_name"]


@pytest.fixture(scope="session")
def dedicated_cpu_compute(ml_client):
    from azure.ai.ml.entities import AmlCompute

    cpu_compute_target = "rag-e2e-cpu"

    try:
        cpu_cluster = ml_client.compute.get(cpu_compute_target)
        logger.info(f"Using existing cluster named {cpu_compute_target}")
    except Exception:
        # Let's create the Azure Machine Learning compute object with the intended parameters
        cpu_cluster = AmlCompute(
            name=cpu_compute_target,
            type="amlcompute",
            size="Standard_E16s_v3", #"Standard_E8d_v4",
            min_instances=0,
            max_instances=4,
            idle_time_before_scale_down=600,
            tier="Dedicated",
        )
        logger.info(f"AMLCompute with name {cpu_cluster.name} will be created, with compute size {cpu_cluster.size}")
        cpu_cluster = ml_client.compute.begin_create_or_update(cpu_cluster).result(timeout=600)

    return cpu_cluster



@pytest.fixture()
def test_data_dir(test_dir):
    test_data_dir = test_dir / "index" / "data"
    logger.info(f"test data directory is {test_data_dir}")
    return test_data_dir


@pytest.fixture(scope="session")
def local_components_base():
    return Path(__file__).parent / "components"


@pytest.fixture(scope="session")
def local_environments_base():
    return Path(__file__).parent / "environments"


@pytest.fixture(scope="session")
def local_azure_ai_generative_base():
    return Path(__file__).parent.parent.parent


@pytest.fixture(scope="session")
def aoai_connection(ai_client, aoai_connection_name):
    """
    Retieve AOAI connection information.
    """
    try:
        return ai_client.connections.get(aoai_connection_name)
    except ResourceNotFoundError:
        error = f"AOAI connection {aoai_connection_name} not found, create a new connection via UI or code (find this message in code)."
        logger.error(error)
        raise ValueError(error)
        # from azure.ai.ml.entities._credentials import ApiKeyConfiguration
        # return ai_client.connections.create_or_update(Connection(
        #     name=aoai_connection_name,
        #     type="azure_open_ai",
        #     target="<insert>",
        #     credentials=ApiKeyConfiguration(
        #         key="<insert>"
        #     ),
        #     metadata={
        #         "ApiVersion": "2023-03-15-preview",
        #         "ApiType": "azure",
        #     }
        # ))


@pytest.fixture(scope="session")
def document_intelligence_connection(ai_client, document_intelligence_connection_name) -> Connection:
    """Retrieve ACS connection information."""
    try:
        return ai_client.connections.get(document_intelligence_connection_name)
    except ResourceNotFoundError:
        error = f"Custom connection {document_intelligence_connection_name} not found, create a new connection via UI or code (find this message in code)."
        logger.error(error)
        raise ValueError(error)
        # Custom Connections not currently supported by SDK.
        # Example UI setup: https://github.com/Azure/azureml-examples/blob/main/sdk/python/generative-ai/rag/notebooks/custom_crack_and_chunk/crack_pdfs_with_azure_document_intelligence.ipynb
        # return ai_client.connections.create_or_update(Connection(
        #     name=document_intelligence_connection_name,
        #     type="custom",
        #     target="<insert>",
        # ))


@pytest.fixture(scope="session")
def acs_connection(ai_client, acs_connection_name):
    """
    Retrieve ACS connection information.

    To register a new connection use azure.ai.ml.MLClient.connections.create
    or AI/ML Workspace UI.
    """
    try:
        return ai_client.connections.get(acs_connection_name)
    except ResourceNotFoundError:
        error = f"Azure Search connection {acs_connection_name} not found, create a new connection via UI or code (find this message in code)."
        logger.error(error)
        raise ValueError(error)
        # from azure.ai.ml.entities._credentials import ApiKeyConfiguration
        # return ai_client.connections.create_or_update(Connection(
        #     name=acs_connection_name,
        #     type="cognitive_search",
        #     target="<insert>",
        #     credentials=ApiKeyConfiguration(
        #         key="<insert>"
        #     ),
        #     metadata={
        #         "ApiVersion": "2023-07-01-preview",
        #     }
        # ))


@pytest.fixture(scope="session")
def free_tier_acs_connection(ai_client) -> dict:
    """
    Retrieve ACS connection information.

    To register a new connection use azure.ai.ml.MLClient.connections.create
    or AI/ML Workspace UI.
    """
    return ai_client.connections.get("free-teir-eastus")


@pytest.fixture(scope="session")
def acs_temp_index(acs_connection, keep_acs_index, acs_index_name):
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents.indexes import SearchIndexClient

    index_name = acs_index_name if acs_index_name is not None else f"azure-ai-generative-test-{uuid.uuid4()}"

    yield index_name

    if keep_acs_index:
        logger.info(f"Keeping index: {index_name}")
    else:
        logger.info(f"Deleting index: {index_name}")
        index_client = SearchIndexClient(
            endpoint=acs_connection.target,
            credential=AzureKeyCredential(acs_connection.credentials.key)
        )
        index_client.delete_index(index_name)


@pytest.fixture(scope="session")
def unstructured_docs_uri_folder():
    # TODO: Put this in gitlfs and upload to workpsaceblobstore if not already registered.
    return "azureml://datastores/workspaceblobstore/paths/test_data/unstructured_files/"


@pytest.fixture(scope="session")
def azureml_registry_client(component_source, azure_credentials):
    from azure.ai.ml import MLClient

    if component_source.startswith("registry:"):
        registry = component_source.split(":")[1]
        return MLClient(credential=azure_credentials, registry_name=registry)
    else:
        return None


@pytest.fixture(scope="session")
def ubuntu_index_environment(local_environments_base):
    from azure.ai.ml.entities import BuildContext, Environment

    return Environment(
        name="ubuntu_index",
        description="MLIndex E2E Test Environment",
        build=BuildContext(path=local_environments_base / "ubuntu_index"),
    )


@pytest.fixture(scope="session")
def git_clone_component(component_source, azureml_registry_client, git_clone_component_local):
    if component_source == "dev":
        return git_clone_component_local

    if component_source.startswith("registry:"):
        return azureml_registry_client.components.get("llm_rag_git_clone")

    raise ValueError(f"Unknown component source: {component_source}")


@pytest.fixture(scope="session")
def git_clone_component_local(ubuntu_index_environment, local_azureml_rag_base):
    from azure.ai.ml import Input, Output, command
    #from azure.ai.ml.entities._job.job_service import JupyterLabJobService

    component = command(
        version="0.0.3.t2",
        name="git_clone",
        display_name="Git Clone",
        description="Clone a git repo to `output_data` path.",
        inputs={
            "git_repository": Input(type="string"),
            "branch_name": Input(type="string", optional=True, description="The branch name to pull from the git repository, default picked by git if not specified."),
            "authentication_key_prefix": Input(type="string", optional=True, description="<PREFIX>-USER and <PREFIX>-PASS are the expected names of two Secrets in the Workspace Key Vault which will be used for authenticated when pulling the given git repo."),
        },
        outputs={
            "output_data": Output(type="uri_folder", mode="upload"),
        },
        code=local_azureml_rag_base / "src",
        command=  # "sleep 99999",
        """python -m azure.ai.generative.index._tasks.git_clone\
        --git-repository ${{inputs.git_repository}}\
        $[[--branch-name ${{inputs.branch_name}}]]\
        $[[--authentication-key-prefix ${{inputs.authentication_key_prefix}}]]\
        --output-data ${{outputs.output_data}}\
        """,
        environment=ubuntu_index_environment
        # services={
        #     'jupyter': JupyterLabJobService(),
        # },
    )

    return component.component


@pytest.fixture(scope="session")
def crack_and_chunk_component(component_source, azureml_registry_client, crack_and_chunk_component_local):
    if component_source == "dev":
        return crack_and_chunk_component_local

    if component_source.startswith("registry:"):
        return azureml_registry_client.components.get("llm_rag_crack_and_chunk")

    raise ValueError(f"Unknown component source: {component_source}")


@pytest.fixture(scope="session")
def crack_and_chunk_component_local(ubuntu_index_environment, local_azureml_rag_base):
    from azure.ai.ml import Input, Output, command
    # from azure.ai.ml.entities._job.job_service import JupyterLabJobService

    component = command(
        version="0.0.7.t2",
        name="crack_and_chunk",
        display_name="Crack and Chunk Data",
        description=
        """Creates chunks no larger than `chunk_size` from `input_data`, extracted document titles are prepended to each chunk

        LLM models have token limits for the prompts passed to them, this is a limiting factor at embedding time and even more limiting at prompt completion time as only so much context can be passed along with instructions to the LLM and user queries.
        Chunking allows splitting source data of various formats into small but coherent snippets of information which can be 'packed' into LLM prompts when asking for answers to user querys related to the sorce documents.

        Supported formats: md, txt, html/htm, pdf, ppt(x), doc(x), xls(x), py""",
        inputs={
            # Input AzureML Data
            "input_data": Input(type="uri_folder", mode="rw_mount"),
            # Files to handle from source
            "input_glob": Input(type="string", default="**/*", description="Limit files opened from `input_data`, defaults to '**/*'"),
            "allowed_extensions": Input(type="string", optional=True, description="Comma separated list of extensions to include, if not provided the default list of supported extensions will be used. e.g. '.md,.txt,.html,.py,.pdf'"),
            # Chunking options
            "chunk_size": Input(type="integer", default=768, description="Maximum number of tokens per chunk."),
            "chunk_overlap": Input(type="integer", default=0, description="Number of tokens to overlap between chunks."),
            "use_rcts": Input(type="boolean", default=True, description="Use langchain RecursiveTextSplitter to split chunks."),
            # Augmentation options
            "data_source_url": Input(type="string", optional=True, description="Base URL to join with file paths to create full source file URL for chunk metadata."),
            "document_path_replacement_regex": Input(type="string", optional=True, description="A JSON string with two fields, 'match_pattern' and 'replacement_pattern' to be used with re.sub on the source url. e.g. '{\"match_pattern\": \"(.*)/articles/(.*)\", \"replacement_pattern\": \"\\1/\\2\"}' would remove '/articles' from the middle of the url."),
            # TODO: Remove summary model input or add connection input.
            "max_sample_files": Input(type="integer", default=-1, description="Maximum number of files to sample from input_data, -1 means no limit."),
        },
        outputs={
            "output_chunks": Output(type="uri_folder"),
        },
        code=local_azureml_rag_base / "src",
        command=
        """python -m azure.ai.generative.index._tasks.crack_and_chunk\
        --input_data ${{inputs.input_data}}\
        --input_glob '${{inputs.input_glob}}'\
        $[[--allowed_extensions ${{inputs.allowed_extensions}}]]\
        --output_title_chunk ${{outputs.output_chunks}}\
        --chunk_size ${{inputs.chunk_size}}\
        --chunk_overlap ${{inputs.chunk_overlap}}\
        --use_rcts ${{inputs.use_rcts}}\
        $[[--data_source_url ${{inputs.data_source_url}}]]\
        $[[--document_path_replacement_regex '${{inputs.document_path_replacement_regex}}']]\
        --max_sample_files ${{inputs.max_sample_files}}\
        """,
        environment=ubuntu_index_environment,
        # services={
        #     'jupyter': JupyterLabJobService(),
        # },
    )

    return component.component


@pytest.fixture(scope="session")
def crack_and_chunk_and_embed_component(component_source, azureml_registry_client, crack_and_chunk_and_embed_component_local):
    if component_source == "dev":
        return crack_and_chunk_and_embed_component_local

    if component_source.startswith("registry:"):
        return azureml_registry_client.components.get("llm_rag_crack_and_chunk_and_embed")

    raise ValueError(f"Unknown component source: {component_source}")


@pytest.fixture(scope="session")
def crack_and_chunk_and_embed_component_local(ubuntu_rag_environment, local_azureml_rag_base):
    from azure.ai.ml import Input, Output, command

    component = command(
        version="0.0.1",
        name="crack_and_chunk_and_embed",
        display_name="Crack, Chunk and Embed Data",
        description=
        """Creates chunks no larger than `chunk_size` from `input_data`, extracted document titles are prepended to each chunk

        LLM models have token limits for the prompts passed to them, this is a limiting factor at embedding time and even more limiting at prompt completion time as only so much context can be passed along with instructions to the LLM and user queries.
        Chunking allows splitting source data of various formats into small but coherent snippets of information which can be 'packed' into LLM prompts when asking for answers to user querys related to the sorce documents.

        Supported formats: md, txt, html/htm, pdf, ppt(x), doc(x), xls(x), py

        Also generates embeddings vectors for data chunks if configured.

        If `embeddings_container` is supplied, input chunks are compared to existing chunks in the Embeddings Container and only changed/new chunks are embedded, existing chunks being reused.
        """,
        inputs={
            # Input AzureML Data
            "input_data": Input(type="uri_folder", mode="rw_mount"),
            # Files to handle from source
            "input_glob": Input(type="string", default="**/*", description="Limit files opened from `input_data`, defaults to '**/*'"),
            # Chunking options
            "chunk_size": Input(type="integer", default=768, description="Maximum number of tokens per chunk."),
            "chunk_overlap": Input(type="integer", default=0, description="Number of tokens to overlap between chunks."),
            "use_rcts": Input(type="boolean", default=True, description="Use langchain RecursiveTextSplitter to split chunks."),
            # Augmentation options
            "citation_url": Input(type="string", optional=True, description="Base URL to join with file paths to create full source file URL for chunk metadata."),
            "citation_replacement_regex": Input(type="string", optional=True, description="A JSON string with two fields, 'match_pattern' and 'replacement_pattern' to be used with re.sub on the source url. e.g. '{\"match_pattern\": \"(.*)/articles/(.*)\", \"replacement_pattern\": \"\\1/\\2\"}' would remove '/articles' from the middle of the url."),
            # Embedding options
            "embeddings_container": Input(type="uri_folder", mode="direct", optional=True, description="Folder containing previously generated embeddings. Should be parent folder of the 'embeddings' output path used for for this component. Will compare input data to existing embeddings and only embed changed/new data, reusing existing chunks."),
            "embeddings_model": Input(type="string", default="hugging_face://model/sentence-transformers/all-mpnet-base-v2", description="The model to use to embed data. E.g. 'hugging_face://model/sentence-transformers/all-mpnet-base-v2' or 'azure_open_ai://deployment/{deployment_name}/model/{model_name}'"),
            "embeddings_connection_id": Input(type="string", description="The connection id of the Embeddings Model provider to use."),
            "batch_size": Input(type="integer", default=100, description="Batch size to use when embedding data."),
            "num_workers": Input(type="integer", default=-1, description="Number of workers to use when embedding data."),
        },
        outputs={
            "embeddings": Output(type="uri_folder", mode="rw_mount", description="Where to save data with embeddings. This should be a subfolder of previous embeddings if supplied, typically named using '${name}'. e.g. /my/prev/embeddings/${name}"),
        },
        code=local_azureml_rag_base / "src",
        command=
        """python -m azureml.rag.tasks.crack_and_chunk_and_embed\
        --input_data ${{inputs.input_data}}\
        --input_glob '${{inputs.input_glob}}'\
        --chunk_size ${{inputs.chunk_size}}\
        --chunk_overlap ${{inputs.chunk_overlap}}\
        --use_rcts ${{inputs.use_rcts}}\
        $[[--citation_url ${{inputs.citation_url}}]]\
        $[[--citation_replacement_regex '${{inputs.citation_replacement_regex}}']]\
        --embeddings_model ${{inputs.embeddings_model}}\
        --embeddings_connection_id ${{inputs.embeddings_connection_id}}\
        $[[--embeddings_container ${{inputs.embeddings_container}}]]\
        --output_path ${{outputs.embeddings}}\
        --batch_size ${{inputs.batch_size}}\
        --num_workers ${{inputs.num_workers}}\
        """,
        environment=ubuntu_rag_environment,
    )

    return component.component


@pytest.fixture(scope="session")
def generate_embeddings_parallel_component(component_source, azureml_registry_client, generate_embeddings_parallel_component_local):
    if component_source == "dev":
        return generate_embeddings_parallel_component_local

    if component_source.startswith("registry:"):
        return azureml_registry_client.components.get("llm_rag_generate_embeddings_parallel")

    raise ValueError(f"Unknown component source: {component_source}")


@pytest.fixture(scope="session")
def generate_embeddings_parallel_component_local(ubuntu_index_environment, local_azureml_rag_base):
    from azure.ai.ml import Input, Output
    from azure.ai.ml.parallel import RunFunction, parallel_run_function

    component = parallel_run_function(
        version="0.0.5.t1",
        name="generate_embeddings_parallel",
        display_name="Generate Embeddings Parallel",
        description=
        """Generates embeddings vectors for data chunks read from `chunks_source`.

        `chunks_source` is expected to contain `csv` files containing two columns:
        - "Chunk" - Chunk of text to be embedded
        - "Metadata" - JSON object containing metadata for the chunk

        If `embeddings_container` is supplied, input chunks are compared to existing chunks in the Embeddings Container and only changed/new chunks are embedded, existing chunks being reused.
        """,
        inputs={
            "chunks_source": Input(type="uri_folder", description="Folder containing chunks to be embedded."),
            "embeddings_container": Input(type="uri_folder", mode="direct", optional=True, description="Folder containing previously generated embeddings. Should be parent folder of the 'embeddings' output path used for for this component. Will compare input data to existing embeddings and only embed changed/new data, reusing existing chunks."),
            "embeddings_model": Input(type="string", default="hugging_face://model/sentence-transformers/all-mpnet-base-v2", description="The model to use to embed data. E.g. 'hugging_face://model/sentence-transformers/all-mpnet-base-v2' or 'azure_open_ai://deployment/{deployment_name}/model/{model_name}'"),
        },
        outputs={
            "embeddings": Output(type="uri_folder", mode="rw_mount", description="Where to save data with embeddings. This should be a subfolder of previous embeddings if supplied, typically named using '${name}'. e.g. /my/prev/embeddings/${name}"),
            "processed_file_names": Output(type="uri_file", mode="rw_mount"),
        },
        input_data="${{inputs.chunks_source}}",
        instance_count=2,
        max_concurrency_per_instance=1,
        mini_batch_size="3",
        mini_batch_error_threshold=1,
        retry_settings={
            "max_retries": 3,
            "timeout": 1200
        },
        logging_level="INFO",
        task=RunFunction(
            code=str(local_azureml_rag_base / "src"),
            entry_script="azureml/rag/tasks/embed_prs.py",
            program_arguments=
            """--output_data ${{outputs.embeddings}}\
            $[[--embeddings_container ${{inputs.embeddings_container}}]]\
            --embeddings_model ${{inputs.embeddings_model}}\
            --task_overhead_timeout 1200\
            --progress_update_timeout 1200\
            --first_task_creation_timeout 600\
            """,
            append_row_to="${{outputs.processed_file_names}}",
            environment=ubuntu_index_environment,
        ),
    )

    return component.component


@pytest.fixture(scope="session")
def generate_embeddings_component(component_source, azureml_registry_client, generate_embeddings_component_local):
    if component_source == "dev":
        return generate_embeddings_component_local

    if component_source.startswith("registry:"):
        return azureml_registry_client.components.get("llm_rag_generate_embeddings")

    raise ValueError(f"Unknown component source: {component_source}")


@pytest.fixture(scope="session")
def generate_embeddings_component_local(ubuntu_index_environment, local_azureml_rag_base):
    from azure.ai.ml import Input, Output, command

    component = command(
        version="0.0.1",
        name="generate_embeddings",
        display_name="Generate Embeddings",
        description=
        """Generates embeddings vectors for data chunks read from `chunks_source`.

        `chunks_source` is expected to contain `csv` files containing two columns:
        - "Chunk" - Chunk of text to be embedded
        - "Metadata" - JSON object containing metadata for the chunk

        If `embeddings_container` is supplied, input chunks are compared to existing chunks in the Embeddings Container and only changed/new chunks are embedded, existing chunks being reused.
        """,
        inputs={
            "chunks_source": Input(type="uri_folder", description="Folder containing chunks to be embedded."),
            "embeddings_container": Input(type="uri_folder", mode="direct", optional=True, description="Folder containing previously generated embeddings. Should be parent folder of the 'embeddings' output path used for for this component. Will compare input data to existing embeddings and only embed changed/new data, reusing existing chunks."),
            "embeddings_model": Input(type="string", default="hugging_face://model/sentence-transformers/all-mpnet-base-v2", description="The model to use to embed data. E.g. 'hugging_face://model/sentence-transformers/all-mpnet-base-v2' or 'azure_open_ai://deployment/{deployment_name}/model/{model_name}'"),
            "batch_size": Input(type="integer", default=100, description="Batch size to use when embedding data."),
            "num_workers": Input(type="integer", default=-1, description="Number of workers to use when embedding data."),
        },
        outputs={
            "embeddings": Output(type="uri_folder", mode="rw_mount", description="Where to save data with embeddings. This should be a subfolder of previous embeddings if supplied, typically named using '${name}'. e.g. /my/prev/embeddings/${name}"),
        },
        code=local_azureml_rag_base / "src",
        command=
        """python -m azure.ai.generative.index._tasks.embed\
        --chunks_source ${{inputs.chunks_source}}\
        --embeddings_model ${{inputs.embeddings_model}}\
        $[[--embeddings_container ${{inputs.embeddings_container}}]]\
        --output ${{outputs.embeddings}}\
        --batch_size ${{inputs.batch_size}}\
        --num_workers ${{inputs.num_workers}}\
        """,
        environment=ubuntu_index_environment,
    )

    return component.component


@pytest.fixture(scope="session")
def create_faiss_index_component(component_source, azureml_registry_client, create_faiss_index_component_local):
    if component_source == "dev":
        return create_faiss_index_component_local

    if component_source.startswith("registry:"):
        return azureml_registry_client.components.get("llm_rag_create_faiss_index")

    raise ValueError(f"Unknown component source: {component_source}")


@pytest.fixture(scope="session")
def create_faiss_index_component_local(ubuntu_index_environment, local_azureml_rag_base):
    from azure.ai.ml import Input, Output, command

    component = command(
        version="0.0.4.t2",
        name="create_faiss_index",
        display_name="Create FAISS Index",
        description=
        """Creates a FAISS index from embeddings. The index will be saved to the output folder.
        The index will be registered as a Data Asset named `asset_name` if `register_output` is set to `True`.""",
        inputs={
            "embeddings": Input(type="uri_folder", mode="direct", description="Folder containing embeddings to be indexed."),
        },
        outputs={
            "index": Output(type="uri_folder"),
        },
        code=local_azureml_rag_base / "src",
        command=
        """python -m azure.ai.generative.index._tasks.build_faiss\
        --embeddings ${{inputs.embeddings}}\
        --output ${{outputs.index}}\
        """,
        environment=ubuntu_index_environment,
    )

    return component.component


@pytest.fixture(scope="session")
def update_acs_index_component(component_source, azureml_registry_client, update_acs_index_component_local):
    if component_source == "dev":
        return update_acs_index_component_local

    if component_source.startswith("registry:"):
        return azureml_registry_client.components.get("llm_rag_update_acs_index")

    raise ValueError(f"Unknown component source: {component_source}")


@pytest.fixture(scope="session")
def update_acs_index_component_local(ubuntu_rag_environment, local_azureml_rag_base):
    from azure.ai.ml import Input, Output, command

    component = command(
        version="0.0.5",
        name="update_acs_index",
        display_name="Update ACS Index",
        description=
        """Uploads `embeddings` into Azure Cognitive Search instance specified in `acs_config`. The Index will be created if it doesn't exist.

        The Index will have the following fields populated:
        - "id", String, key=True
        - "content", String,
        - "content_vector_(open_ai|hugging_face)", Collection(Single)
        - "category", String
        - "sourcepage", String
        - "sourcefile", String
        - "content_hash", String
        - "meta_json_string", String

        "meta_json_string" contains all metadata for a document serialized as a JSON string.
        """,
        inputs={
            "embeddings": Input(type="uri_folder", mode="direct", description="Embeddings output produced from generate_embeddings_parallel."),
            "acs_config": Input(type="string", description='JSON string containing the ACS configuration. e.g. {"index_name": "my-index"}'),
            "connection_id": Input(type="string", optional=True, description="The connection id of the ACS provider to use."),
        },
        outputs={
            "index": Output(type="uri_folder"),
        },
        code=local_azureml_rag_base / "src",
        command=
        """python -m azureml.rag.tasks.update_acs\
        --embeddings ${{inputs.embeddings}}\
        --acs_config '${{inputs.acs_config}}'\
        $[[--connection_id '${{inputs.connection_id}}']]\
        --output ${{outputs.index}}\
        """,
        environment=ubuntu_rag_environment,
    )

    return component.component


@pytest.fixture(scope="session")
def register_mlindex_asset_component(component_source, azureml_registry_client, register_mlindex_asset_component_local):
    if component_source == "dev":
        return register_mlindex_asset_component_local

    if component_source.startswith("registry:"):
        return azureml_registry_client.components.get("llm_rag_register_mlindex_asset")

    raise ValueError(f"Unknown component source: {component_source}")


@pytest.fixture(scope="session")
def register_mlindex_asset_component_local(ubuntu_index_environment, local_azureml_rag_base):
    from azure.ai.ml import Input, Output, command

    component = command(
        version="0.0.3.t2",
        name="register_mlindex_asset",
        display_name="Register MLIndex Asset",
        description=
        """Creates a FAISS index from embeddings. The index will be saved to the output folder.
        The index will be registered as a Data Asset named `asset_name` if `register_output` is set to `True`.""",
        inputs={
            "storage_uri": Input(type="uri_folder", mode="direct", description="Folder containing MLIndex to be registered."),
            "asset_name": Input(type="string", description="Name of MLIndex asset to register."),
        },
        outputs={
            "asset_id": Output(type="uri_file"),
        },
        code=local_azureml_rag_base / "src",
        command=
        """python -m azure.ai.generative.index._tasks.register_mlindex\
        --storage-uri ${{inputs.storage_uri}}\
        --asset-name ${{inputs.asset_name}}\
        --output-asset-id ${{outputs.asset_id}}\
        """,
        environment=ubuntu_index_environment,
    )

    return component.component


@pytest.fixture(scope="session")
def qa_data_generation_component(component_source, azureml_registry_client, qa_data_generation_component_local):
    if component_source == "dev":
        return qa_data_generation_component_local

    if component_source.startswith("registry:"):
        return azureml_registry_client.components.get("llm_rag_qa_data_generation")

    raise ValueError(f"Unknown component source: {component_source}")


@pytest.fixture(scope="session")
def qa_data_generation_component_local(ubuntu_index_environment, local_azureml_rag_base):
    from azure.ai.ml import Input, Output, command

    component = command(
        version="0.0.0.t0",
        name="qa_data_generation",
        display_name="LLM - Generate QnA Test Data",
        description="LLM - Generate QnA Test Data",
        inputs={
            "input_data": Input(type="uri_folder"),
            "dataset_size": Input(type="integer", default=100),
            "chunk_batch_size": Input(type="integer", default=2),
            "llm_config": Input(type="string", default='{"type": "azure_open_ai","model_name": "gpt-35-turbo", "deployment_name": "gpt-35-turbo", "temperature": 0, "max_tokens": 3000}'),
            "output_format": Input(type="string", default="json"),
            "qa_types": Input(type="string", default="SHORT_ANSWER,LONG_ANSWER,BOOLEAN,SUMMARY,CONVERSATION"),
            "openai_api_version": Input(type="string", default="2023-03-15-preview"),
            "openai_api_type": Input(type="string", default="azure"),
        },
        outputs={
            "output_data": Output(type="uri_folder", mode="rw_mount"),
        },
        code=f"{local_azureml_rag_base}\\src",  # convert Path() to string to avoid a bug where code directory isn't uploaded
        command="""python -m azure.ai.generative.index._tasks.generate_qa \
            --input-data ${{inputs.input_data}} \
            --output-data ${{outputs.output_data}} \
            --dataset_size ${{inputs.dataset_size}} \
            --chunk_batch_size ${{inputs.chunk_batch_size}} \
            --llm_config '${{inputs.llm_config}}' \
            --output_format '${{inputs.output_format}}' \
            --qa_types '${{inputs.qa_types}}' \
            --openai_api_version '${{inputs.openai_api_version}}' \
            --openai_api_type '${{inputs.openai_api_type}}' \
        """,
        environment=ubuntu_index_environment,
    )

    return component.component
