from azure.synapse import SynapseClient
from azure.identity import ClientSecretCredential


class SynapseSamples:

    def __init__(self):
        self.synapse_client = self.synapse_data_plane_factory()
        self.spark_batch_operation = self.synapse_client.spark_batch

    @staticmethod
    def synapse_data_plane_factory():
        credential = ClientSecretCredential(
            tenant_id="", # your tenant id
            client_id="", #  your client id
            client_secret="", # your client secret
        )
        return SynapseClient(credential)

    # Scenario 1: List all spark batch job under specific spark pool
    def list_spark_batch_jobs(self, spark_pool_name, workspace_name, detailed=True):
        self.spark_batch_operation.list(workspace_name=workspace_name, spark_pool_name=spark_pool_name,
                                        detailed=detailed)

    # Scenario 2: Get a specific spark batch job with batch id
    def get_spark_batch_job(self, batch_id, spark_pool_name, workspace_name, detailed=True):
        self.spark_batch_operation.get(workspace_name=workspace_name, spark_pool_name=spark_pool_name,
                                       batch_id=batch_id)

    # Scenario 3: Submit/Create a spark batch job
    def create_spark_batch_job(self, workspace_name, spark_pool_name, job_name, file, class_name,
                               args, driver_memory, driver_cores, executor_memory, executor_cores,
                               num_executors, jars=None, files=None, archives=None, conf=None, artifact_id=None,
                               tags=None, detailed=True):
        from azure.synapse.models import ExtendedLivyBatchRequest

        livy_batch_request = ExtendedLivyBatchRequest(
            tags=tags, artifact_id=artifact_id,
            name=job_name, file=file, class_name=class_name, args=args, jars=jars, files=files, archives=archives,
            conf=conf, driver_memory=driver_memory, driver_cores=driver_cores, executor_memory=executor_memory,
            executor_cores=executor_cores, num_executors=num_executors)

        return self.spark_batch_operation.create(workspace_name, spark_pool_name, livy_batch_request, detailed)

    # Scenario 4: Delete/Cancel a spark batch job
    def cancel_spark_batch_job(self, batch_id, spark_pool_name, workspace_name, detailed=True):
        self.spark_batch_operation.delete(workspace_name=workspace_name, spark_pool_name=spark_pool_name,
                                          batch_id=batch_id)


if __name__ == "__main__":
    synapse_sample = SynapseSamples()
    workspace_name = "testsynapseworkspace"
    spark_pool_name = "testsparkpool"
    batch_id = 1
    # parameter for creating batch job
    job_name = "WordCount_Java"
    file = "abfss://{filesystem}@{adlsgen2account}.dfs.core.windows.net/samples/java/wordcount/wordcount.jar"
    class_name = "WordCount"
    args = ["abfss://{filesystem}@{adlsgen2account}.dfs.core.windows.net/samples/java/wordcount/shakespeare.txt",
            "abfss://{filesystem}@{adlsgen2account}.dfs.core.windows.net/samples/java/wordcount/result/"]
    driver_memory = "4g"
    driver_cores = 4
    executor_memory = "4g"
    executor_cores = 4
    num_executors = 2

    # list
    batch_jobs = synapse_sample.list_spark_batch_jobs(spark_pool_name, workspace_name)

    # get
    batch_job = synapse_sample.get_spark_batch_job(batch_id, spark_pool_name, workspace_name)

    # Create
    submit_result_job = synapse_sample.create_spark_batch_job(workspace_name, spark_pool_name, job_name, file,
                                                              class_name, args, driver_memory, driver_cores,
                                                              executor_memory, executor_cores, num_executors)

    # Cancel batch job
    synapse_sample.cancel_spark_batch_job(submit_result_job.id, submit_result_job.spark_pool_name,
                                          submit_result_job.workspace_name)
