.. :changelog:

Release History
===============

3.0.0 (2019-02-07)
++++++++++++++++++

**Features**

- Model NotificationChannel has a new parameter email_recipient
- Model NotificationChannel has a new parameter notification_locale
- Model ArtifactInstallProperties has a new parameter artifact_title
- Model GalleryImage has a new parameter plan_id
- Model GalleryImage has a new parameter is_plan_authorized
- Model EvaluatePoliciesProperties has a new parameter user_object_id
- Model ArtifactInstallPropertiesFragment has a new parameter artifact_title
- Model Lab has a new parameter announcement
- Model Lab has a new parameter support
- Model Lab has a new parameter load_balancer_id
- Model Lab has a new parameter mandatory_artifacts_resource_ids_linux
- Model Lab has a new parameter extended_properties
- Model Lab has a new parameter mandatory_artifacts_resource_ids_windows
- Model Lab has a new parameter vm_creation_resource_group
- Model Lab has a new parameter environment_permission
- Model Lab has a new parameter network_security_group_id
- Model Lab has a new parameter public_ip_id
- Model NotificationSettingsFragment has a new parameter email_recipient
- Model NotificationSettingsFragment has a new parameter notification_locale
- Model LabVirtualMachineCreationParameter has a new parameter schedule_parameters
- Model LabVirtualMachineCreationParameter has a new parameter compute_id
- Model LabVirtualMachineCreationParameter has a new parameter data_disk_parameters
- Model LabVirtualMachineCreationParameter has a new parameter last_known_power_state
- Model LabVirtualMachineCreationParameter has a new parameter plan_id
- Model ShutdownNotificationContent has a new parameter vm_url
- Model ShutdownNotificationContent has a new parameter minutes_until_shutdown
- Model NotificationSettings has a new parameter email_recipient
- Model NotificationSettings has a new parameter notification_locale
- Model LabVirtualMachine has a new parameter plan_id
- Model LabVirtualMachine has a new parameter schedule_parameters
- Model LabVirtualMachine has a new parameter last_known_power_state
- Model LabVirtualMachine has a new parameter data_disk_parameters
- Model ArmTemplate has a new parameter enabled
- Model CustomImage has a new parameter custom_image_plan
- Model CustomImage has a new parameter data_disk_storage_info
- Model CustomImage has a new parameter is_plan_authorized
- Model CustomImage has a new parameter managed_snapshot_id
- Model LabVirtualMachineFragment has a new parameter schedule_parameters
- Model LabVirtualMachineFragment has a new parameter compute_id
- Model LabVirtualMachineFragment has a new parameter data_disk_parameters
- Model LabVirtualMachineFragment has a new parameter last_known_power_state
- Model LabVirtualMachineFragment has a new parameter plan_id
- Added operation DisksOperations.update
- Added operation CustomImagesOperations.update
- Added operation LabsOperations.import_virtual_machine
- Added operation SecretsOperations.update
- Added operation EnvironmentsOperations.update
- Added operation FormulasOperations.update
- Added operation VirtualMachinesOperations.transfer_disks
- Added operation VirtualMachinesOperations.un_claim
- Added operation VirtualMachinesOperations.resize
- Added operation VirtualMachinesOperations.restart
- Added operation VirtualMachinesOperations.get_rdp_file_contents
- Added operation VirtualMachinesOperations.redeploy
- Added operation group ServiceFabricsOperations
- Added operation group ServiceFabricSchedulesOperations

**Breaking changes**

- Model VirtualNetworkFragment no longer has parameter type
- Model VirtualNetworkFragment no longer has parameter id
- Model VirtualNetworkFragment no longer has parameter location
- Model VirtualNetworkFragment no longer has parameter name
- Model VirtualNetworkFragment no longer has parameter external_subnets
- Model VirtualNetworkFragment no longer has parameter provisioning_state
- Model VirtualNetworkFragment no longer has parameter unique_identifier
- Model PolicyFragment no longer has parameter type
- Model PolicyFragment no longer has parameter id
- Model PolicyFragment no longer has parameter location
- Model PolicyFragment no longer has parameter name
- Model PolicyFragment no longer has parameter unique_identifier
- Model PolicyFragment no longer has parameter provisioning_state
- Model ArtifactSourceFragment no longer has parameter type
- Model ArtifactSourceFragment no longer has parameter id
- Model ArtifactSourceFragment no longer has parameter location
- Model ArtifactSourceFragment no longer has parameter name
- Model ArtifactSourceFragment no longer has parameter unique_identifier
- Model ArtifactSourceFragment no longer has parameter provisioning_state
- Model LabVirtualMachineCreationParameter no longer has parameter applicable_schedule
- Model LabVirtualMachineCreationParameter no longer has parameter compute_vm
- Model LabVirtualMachineCreationParameter no longer has parameter unique_identifier
- Model LabVirtualMachineCreationParameter no longer has parameter provisioning_state
- Model ApplicableScheduleFragment no longer has parameter location
- Model ApplicableScheduleFragment no longer has parameter type
- Model ApplicableScheduleFragment no longer has parameter id
- Model ApplicableScheduleFragment no longer has parameter name
- Model ScheduleFragment no longer has parameter type
- Model ScheduleFragment no longer has parameter id
- Model ScheduleFragment no longer has parameter location
- Model ScheduleFragment no longer has parameter name
- Model ScheduleFragment no longer has parameter unique_identifier
- Model ScheduleFragment no longer has parameter provisioning_state
- Model LabVirtualMachineFragment no longer has parameter type
- Model LabVirtualMachineFragment no longer has parameter id
- Model LabVirtualMachineFragment no longer has parameter compute_vm
- Model LabVirtualMachineFragment no longer has parameter location
- Model LabVirtualMachineFragment no longer has parameter name
- Model LabVirtualMachineFragment no longer has parameter unique_identifier
- Model LabVirtualMachineFragment no longer has parameter provisioning_state
- Model LabVirtualMachineFragment no longer has parameter applicable_schedule
- Model LabFragment has a new signature
- Model UserFragment has a new signature
- Model NotificationChannelFragment has a new signature

2.2.0 (2018-02-15)
++++++++++++++++++

* Add "providers" operation group

2.1.0 (2017-10-25)
++++++++++++++++++

* Add "operations" operation group

2.0.0 (2017-04-27)
++++++++++++++++++

* Major refactoring to follow name conventions + new features.
* This wheel package is now built with the azure wheel extension

1.0.0 (2016-09-13)
++++++++++++++++++

* Initial Release
