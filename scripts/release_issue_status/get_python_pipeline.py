import os
import re

from msrest.authentication import BasicAuthentication
from azure.devops.v6_0.pipelines.pipelines_client import PipelinesClient


def get_python_pipelines():
    python_piplines = {}
    pipeline_client = PipelinesClient(base_url='https://dev.azure.com/azure-sdk',
                                      creds=BasicAuthentication('', os.getenv('PIPELINE_TOKEN')))
    pipelines = pipeline_client.list_pipelines(project='internal')
    for pipeline in pipelines:
        if re.findall('^python - \w*$', pipeline.name):
            key = pipeline.name.replace('python - ', '')
            python_piplines[key] = pipeline.id
    return python_piplines


def get_pipeline_url(python_piplines, output_folder):
    definitionId = python_piplines.get(output_folder)
    if definitionId:
        pipeline_url = 'https://dev.azure.com/azure-sdk/internal/_build?definitionId={}'.format(definitionId)
    else:
        print('Cannot find definitionId, Do not display pipeline_url')
        pipeline_url = ''
    return pipeline_url
