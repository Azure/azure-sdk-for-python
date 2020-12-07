def main():
    from azure.synapse.artifacts import ArtifactsClient
    from azure.identity import DefaultAzureCredential

    endpoint = "https://xysynapsetest.dev.azuresynapse.net"  # "WorkspaceUrl"
    pipeline_name = "demo_pipeline"

    client = ArtifactsClient(credential=DefaultAzureCredential(),
                             endpoint=endpoint)

    run = client.pipeline.create_pipeline_run(pipeline_name=pipeline_name)
    print("Pipeline run is created, id: {0}".format(run.run_id))

if __name__ == "__main__":
    main()