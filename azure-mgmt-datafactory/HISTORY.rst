.. :changelog:

Release History
===============

0.6.0 (2018-03-22)
++++++++++++++++++

- Added new AzureDatabricks LinkedService and DatabricksNotebook Activity
- Added headNodeSize and dataNodeSize properties in HDInsightOnDemand LinkedService
- Added LinkedService, Dataset, CopySource for SalesforceMarketingCloud
- Added support for SecureOutput on all activities
- Added new BatchCount property on ForEach activity which controls how many concurrent activities to run
- Added DELETE method for Web Activity
- Added new Filter Activity
- Added Linked Service Parameters support

0.5.0 (2018-02-16)
++++++++++++++++++

- Enable AAD auth via service principal and management service identity for Azure SQL DB/DW linked service types
- Support integration runtime sharing across subscription and data factory
- Enable Azure Key Vault for all compute linked service
- Add SAP ECC Source
- GoogleBigQuery support clientId and clientSecret for UserAuthentication
- Add LinkedService, Dataset, CopySource for Vertica and Netezza

0.4.0 (2018-02-02)
++++++++++++++++++

**Features**

- Add readBehavior to Salesforce Source
- Enable Azure Key Vault support for all data store linked services
- Add license type property to Azure SSIS integration runtime

0.3.0 (2017-12-12)
++++++++++++++++++

**Features**

- Add SAP Cloud For Customer Source 
- Add SAP Cloud For Customer Dataset 
- Add SAP Cloud For Customer Sink 
- Support providing a Dynamics password as a SecureString, a secret in Azure Key Vault, or as an encrypted credential. 
- App model for Tumbling Window Trigger 
- Add LinkedService, Dataset, Source for 26 RFI connectors, including: PostgreSQL,Google BigQuery,Impala,ServiceNow,Greenplum/Hawq,HBase,Hive ODBC,Spark ODBC,HBase Phoenix,MariaDB,Presto,Couchbase,Concur,Zoho CRM,Amazon Marketplace Services,PayPal,Square,Shopify,QuickBooks Online,Hubspot,Atlassian Jira,Magento,Xero,Drill,Marketo,Eloqua. 
- Support round tripping of new properties using additionalProperties for some types 
- Add new integration runtime API's: patch integration runtime; patch integration runtime node; upgrade integration runtime, get node IP address 
- Add integration runtime naming validation 

0.2.2 (2017-11-13)
++++++++++++++++++

**Features**

- Added new connectors: AzureMySql, Salesforce and JSONFormat, Dynamics Sink
- Added support providing Salesforce passwords and security tokens as SecureString and AzureKeyVaultSecret for Dynamics/Salesforce
- Added cancel pipeline run api

0.2.1 (2017-10-03)
++++++++++++++++++

**Features**

- Add factories.cancel_pipeline_run

0.2.0 (2017-09-22)
++++++++++++++++++

* Initial Release
