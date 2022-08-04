# Microsoft Azure SDK for Python

This is the Microsoft Azure Auto Manage Management Client Library.
This package has been tested with Python 3.7+.
For a more complete view of Azure libraries, see the [azure sdk python release](https://aka.ms/azsdk/python/all).

## _Disclaimer_

_Azure SDK Python packages support for Python 2.7 has ended 01 January 2022. For more information and questions, please refer to https://github.com/Azure/azure-sdk-for-python/issues/20691_

# Usage

## Examples

#### Instantiate an Automanage Client

Install the Azure Identity and Azure Automanage modules
`pip install azure-identity`
`pip install azure-mgmt-automanage==1.0.0`

```python
from azure.identity import DefaultAzureCredential
from azure.mgmt.automanage import AutomanageClient

credential = DefaultAzureCredential()
client = automanage.AutomanageClient(credential, "<subscription ID>")
```

#### Create or Update a Custom Automanage Configuration Profile

Create or update a custom configuration profile by modifying the **ConfigurationProfile** properties.

 ```python
new_profile = {
    "location": "eastus",
    "tags": {},
    "properties": {
        "configuration": {
            "Antimalware/Enable": True,
            "Antimalware/EnableRealTimeProtection": True,
            "Antimalware/RunScheduledScan": True,
            "Antimalware/ScanType": "Quick",
            "Antimalware/ScanDay": 7,
            "Antimalware/ScanTimeInMinutes": 120,
            "Backup/Enable": True,
            "Backup/PolicyName": "dailyBackupPolicy",
            "Backup/TimeZone": "UTC",
            "Backup/InstantRpRetentionRangeInDays": 2,
            "Backup/SchedulePolicy/ScheduleRunFrequency": "Daily",
            "Backup/SchedulePolicy/SchedulePolicyType": "SimpleSchedulePolicy",
            "Backup/RetentionPolicy/RetentionPolicyType": "LongTermRetentionPolicy",
            "Backup/RetentionPolicy/DailySchedule/RetentionDuration/Count": 180,
            "Backup/RetentionPolicy/DailySchedule/RetentionDuration/DurationType": "Days",
            "WindowsAdminCenter/Enable": False,
            "VMInsights/Enable": True,
            "AzureSecurityCenter/Enable": True,
            "UpdateManagement/Enable": True,
            "ChangeTrackingAndInventory/Enable": True,
            "GuestConfiguration/Enable": True,
            "AutomationAccount/Enable": True,
            "LogAnalytics/Enable": True,
            "BootDiagnostics/Enable": True
        }
    }
}

client.configuration_profiles.create_or_update("configurationProfileName", "resourceGroupName", new_profile)
 ```

 #### Get an Automanage Configuration Profile

 ```python
profile = client.configuration_profiles.get("configurationProfileName", "resourceGroupName")
 ```

#### Delete an Automanage Configuration Profile

 ```python
client.configuration_profiles.delete("resourceGroupName", "configurationProfileName")
 ```

#### Get an Automanage Profile Assignment

```python 
assignment = client.configuration_profile_assignments.get("resourceGroupName", "default", "vmName")
```

#### Create an Assignment between a VM and an Automanage Best Practices Production Configuration Profile
 
The **Best Practices Profile** live at the tenant scope, so the **configurationProfile** path would be: `/providers/Microsoft.Automanage/bestPractices/AzureBestPracticesProduction`

 ```python 
assignment = {
    "properties": {
        "configurationProfile": "/providers/Microsoft.Automanage/bestPractices/AzureBestPracticesProduction",
    }
}

# assignment name must be named 'default'
client.configuration_profile_assignments.create_or_update("default", "resourceGroupName", "vmName", assignment)
 ```

#### Create an Assignment between a VM and a Custom Automanage Configuration Profile

**Custom Profiles** live within resource groups, so the **configurationProfile** path would be: `/subscriptions/<sub ID>/resourceGroups/resourceGroupName/providers/Microsoft.Automanage/configurationProfiles/configurationProfileName`


```python
assignment = {
    "properties": {
        "configurationProfile": "/subscriptions/<sub ID>/resourceGroups/resourceGroupName/providers/Microsoft.Automanage/configurationProfiles/configurationProfileName"
    }
}

# assignment name must be named 'default'
client.configuration_profile_assignments.create_or_update("default", "resourceGroupName", "vmName", assignment)

```

To learn how to use this package, see the [quickstart guide](https://aka.ms/azsdk/python/mgmt)
 
For docs and references, see [Python SDK References](https://docs.microsoft.com/python/api/overview/azure/)
Code samples for this package can be found at [Auto Manage Management](https://docs.microsoft.com/samples/browse/?languages=python&term=Getting%20started%20-%20Managing&terms=Getting%20started%20-%20Managing) on docs.microsoft.com.
Additional code samples for different Azure services are available at [Samples Repo](https://aka.ms/azsdk/python/mgmt/samples)


# Provide Feedback

If you encounter any bugs or have suggestions, please file an issue in the
[Issues](https://github.com/Azure/azure-sdk-for-python/issues)
section of the project. 


![Impressions](https://azure-sdk-impressions.azurewebsites.net/api/impressions/azure-sdk-for-python%2Fazure-mgmt-automanage%2FREADME.png)
