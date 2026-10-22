$schema: http://azureml/sdk-2-0/DataImport.json
type: mltable
name: my_azuresqldb_asset

source:
  type: database
  query: select * from region
  connection: azureml:my_azuresqldb_connection

path: azureml://datastores/workspaceblobstore/paths/{name}