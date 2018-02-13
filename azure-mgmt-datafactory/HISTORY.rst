.. :changelog:

Release History
===============

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
