# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from azure.identity import DefaultAzureCredential
from azure.mgmt.automanage import AutomanageClient

sub = "<sub ID>"
rg = "resourceGroupName"
profile_name = "custom-profile"
vm = "vmName"


# ------------------------- SET UP AUTOMANAGE CLIENT ---------------------------------------------------
credential = DefaultAzureCredential()
client = AutomanageClient(credential, sub)


# ------------------------ GET PROFILE  ----------------------------------------------------------------
profile = client.configuration_profiles.get(profile_name, rg)
print(profile)


# ------------------------ GET ALL PROFILES IN RESOURCE GROUP  -----------------------------------------
profiles = client.configuration_profiles.list_by_resource_group(rg)
for profile in profiles:
    print(profile)


# ------------------------ GET ALL PROFILES IN SUBSCRIPTION  -------------------------------------------
profiles = client.configuration_profiles.list_by_subscription()
for profile in profiles:
    print(profile)


# ------------------------ CREATE OR UPDATE CUSTOM PROFILE  --------------------------------------------
new_profile = {
    "id": f"/subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.Automanage/configurationProfiles/{profile_name}",
    "name": profile_name,
    "type": "Microsoft.Automanage/configurationProfiles",
    "location": "eastus",
    "tags": {"environment": "dev"},
    "properties": {
        "configuration": {
            "Antimalware/Enable": True,
            "Antimalware/Exclusions/Paths": "",
            "Antimalware/Exclusions/Extensions": "",
            "Antimalware/Exclusions/Processes": "",
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
            "Backup/SchedulePolicy/ScheduleRunTimes": [
                "2022-07-21T12: 00: 00Z"
            ],
            "Backup/SchedulePolicy/SchedulePolicyType": "SimpleSchedulePolicy",
            "Backup/RetentionPolicy/RetentionPolicyType": "LongTermRetentionPolicy",
            "Backup/RetentionPolicy/DailySchedule/RetentionTimes": [
                "2022-07-21T12: 00: 00Z"
            ],
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

client.configuration_profiles.create_or_update(
    profile_name, rg, new_profile)


# ------------------------ DELETE PROFILE  -------------------------------------------------------------
client.configuration_profiles.delete(rg, profile_name)


# ------------------------ GET ASSIGNMENT  -------------------------------------------------------------
assignment = client.configuration_profile_assignments.get(rg, "default", vm)
print(assignment)


# ------------------------ GET ALL ASSIGNMENTS IN RESOURCE GROUP  --------------------------------------
assignments = client.configuration_profile_assignments.list(rg)
for assignment in assignments:
    print(assignment)


# ------------------------ CREATE BEST PRACTICES PRODUCTION PROFILE ASSIGNMENT -------------------------
best_practices_assignment = {
    "id": f"/subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.Compute/virtualMachines/{vm}/providers/Microsoft.Automanage/AutomanageAssignments/default",
    "name": "default",
    "properties": {
          "targetId": f"/subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.Compute/virtualMachines/{vm}",
          "configurationProfile": f"/providers/Microsoft.Automanage/bestPractices/AzureBestPracticesProduction",
    }
}

client.configuration_profile_assignments.create_or_update(
    "default", rg, vm, best_practices_assignment)


# ------------------------ CREATE CUSTOM PROFILE ASSIGNMENT --------------------------------------------
custom_profile_assignment = {
    "id": f"/subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.Compute/virtualMachines/{vm}/providers/Microsoft.Automanage/AutomanageAssignments/default",
    "name": "default",
    "properties": {
        "targetId": f"/subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.Compute/virtualMachines/{vm}",
        "configurationProfile": f"/subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.Automanage/configurationProfiles/{profile_name}"
    }
}

client.configuration_profile_assignments.create_or_update(
    "default", rg, vm, custom_profile_assignment)
