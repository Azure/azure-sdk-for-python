Batch
=====

For more information on the Azure Batch service, check out the `Batch Documentation <https://azure.microsoft.com/en-us/documentation/services/batch/>`__.
For working samples, see the `Batch samples repo <https://github.com/Azure/azure-batch-samples/tree/master/Python>`__.

Create the Batch client
-----------------------

The following code creates an instance of the Batch client.
The Batch client provides access to create pools, manage and schedule jobs, and access compute nodes.

A Batch Account that allows the Batch Service to allocate pools can be authenticated either via
Shared Key authentication, or an Azure Active Directory token. Batch Accounts configured to
allocate pools into the users subscription must be authenticated with an Azure Active Directory token.

For more information on creating and managing Batch accounts, including retrieving account URL and keys,
and pool allocation modes, see the :doc:`Batch Management Client <resourcemanagementbatch>`.


Shared Key Authentication
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    from azure.batch import BatchServiceClient
    from azure.batch.batch_auth import SharedKeyCredentials

    credentials = SharedKeyCredentials(BATCH_ACCOUNT_NAME, BATCH_ACCOUNT_KEY)
    batch_client = BatchServiceClient(
        credentials,
        base_url=BATCH_ACCOUNT_URL
    )

Azure Active Directory Authentication
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    from azure.batch import BatchServiceClient
    from azure.common.credentials import ServicePrincipalCredentials

    credentials = ServicePrincipalCredentials(
        client_id=CLIENT_ID,
        secret=SECRET,
        tenant=TENANT_ID,
        resource="https://batch.core.windows.net/"
    )
	batch_client = BatchServiceClient(
        credentials,
        base_url=BATCH_ACCOUNT_URL
    )

Manage Pools and Nodes
-----------------------

The Batch Client allows you to create, modify, and delete Batch Pools.
You can find more information on pools in this `overview of Azure Batch features <https://azure.microsoft.com/en-us/documentation/articles/batch-api-basics/#pool>`__.

.. code:: python

	# Create a new pool of Windows nodes from Cloud Services
	pool_config = batch.models.CloudServiceConfiguration(os_family='4')
	new_pool = batch.models.PoolAddParameter(
		'my_pool',
		'small',
		cloud_service_configuration=pool_config,
		target_dedicated=3
	)

	batch_client.pool.add(new_pool)
	
	# Create a new pool with Linux nodes using Azure Virtual Machines
	# Marketplace images. For full example, see the Batch samples repo.
	pool = batch.models.PoolAddParameter( 
        id='my_pool', 
        enable_inter_node_communication=True, 
        virtual_machine_configuration=batch.models.VirtualMachineConfiguration( 
            image_reference=MY_IMAGE_REF, 
            node_agent_sku_id=MY_NODE_AGENT), 
        vm_size='small', 
        target_dedicated=6, 
        start_task=batch.models.StartTask( 
            command_line=STARTTASK_RESOURCE_FILE, 
            run_elevated=True, 
            wait_for_success=True, 
            resource_files=[ 
                batch.models.ResourceFile( 
                    file_path=STARTTASK_RESOURCE_FILE, blob_source=SAS_URL)
            ]), 
    )
	batch_client.pool.add(new_pool)



Existing pools can be upgraded, patched, and resized.
You can change the size of a pool either explicitly, or via an auto-scaling formula.
For more information, see this article on `automatically scaling nodes in a Batch pool <https://azure.microsoft.com/en-us/documentation/articles/batch-automatic-scaling/>`__.

.. code:: python

	# Resize an existing pool to a specific number of VMs
	resize = batch.models.PoolResizeParameter(target_dedicated=5)
	batch_client.pool.resize('my_pool', resize)

	# Or set a formula to allow the pool to auto-scale
	autoscale_interval = datetime.timedelta(minutes=10)
	batch_client.pool.enable_auto_scale(
		'my_pool',
		auto_scale_formula='$TargetDedicated = (time().weekday==1?5:1);'
		auto_scale_evaluation_interval=autoscale_interval
	)

	# Update or patch a pool. Note that when updating, all pool parameters must be updated,
	# but when patching, individual parameters can be selectively updated.
	updated_info=batch.models.PoolPatchPropertiesParameter(
		metadata=[batch.models.MetadataItem('foo', 'bar')]
	)
	batch_client.pool.patch('my_pool', updated_info)

	# Upgrade pool OS
	batch_client.pool.upgrade_os('my_pool', 'WA-GUEST-OS-4.28_201601-01')

	

You can monitor pools by retrieving data individually, or grouped using OData filters.
You can learn more about filters with this article on `querying the Batch service efficiently <https://azure.microsoft.com/en-us/documentation/articles/batch-efficient-list-queries/>`__.
You can also retrieve statistics on the usage of a specific pool, or all the pools in the lifetime of your Batch account.

.. code:: python

	if batch_client.pool.exists('my_pool'):
		my_pool = batch_client.pool.get('my_pool')
		print("Current state: {}".format(my_pool.allocation_state))

	# List all pools in the Batch account
	pools = batch_client.pool.list()
	all_pools = [p.id for p in pools]

	# Or retrieve just a selection of pools
	options = batch.models.PoolListOptions(filter='startswith(id,\'my_\')')
	my_pools = batch_client.pool.list(options)
	only_my_pools = [p.id for p in my_pools]

	stats = batch_client.pool.get_all_pools_lifetime_statistics()
	print("Average CPU usage across pools: {}%".format(stats.resource_stats.avg_cpu_percentage))



The Batch client also allows you to access individual nodes within a pool.

.. code:: python

	# List compute nodes in a pool, then remove any erroring ones
	nodes = list(batch_client.compute_node.list())
	errored = [n.id for n in nodes if n.state == batch.models.ComputeNodeState.unusable]
	working_nodes = [n.id for n in nodes if n not in errored]
	batch_client.pool.remove_nodes('my_pool', batch.models.NodeRemoveParameter(errored))

	# Add a user account to a Windows Cloud Services node and retrieve an RDP file
	user = batch.models.ComputeNodeUser('MyTestUser', password='kt#_gahr!@aGERDXA')
	batch_client.compute_node.add_user('my_pool', working_nodes[0], user)
	with open('node.rdp', 'w') as rdp_file:
		data = batch_client.compute_node.get_remote_desktop('my_pool', working_nodes[0])
		for chunk in data:
			rdp_file.write(chunk)
			
	# Add a user to a Linux node and retrieve login settings
	# For full sample see the Batch samples repo
	batch_client.compute_node.add_user( 
		'my_pool', 
		working_nodes[0], 
		batch.models.ComputeNodeUser( 
			'MyTestUser', 
			is_admin=True, 
			password=None, 
			ssh_public_key=SSH_PUBLIC_KEY
	)
	login_details = batch_client.compute_node.get_remote_login_settings(
		'my_pool',
		working_nodes[0]
	)
	print("Remote IP: {}".format(login_details.remote_login_ip_address))
	print("SSH Port: {}".format(login_details.remote_login_port))

	# Reboot or reimage a node
	batch_client.compute_node.reimage('my_pool', working_nodes[1])
	batch_client.compute_node.reboot('my_pool', working_nodes[2])

	

Manage Jobs and Tasks
---------------------

You can create new jobs and add tasks, monitor existing jobs and download outputs.
You can also set up job schedules for future or recurring jobs.

.. code:: python

	# Create Job
	job = batch.models.JobAddParameter(
		'python_test_job',
		batch.models.PoolInformation(pool_id='my_pool')
	)
	batch_client.job.add(job)

	# Add a task
	task = batch.models.TaskAddParameter(
		'python_task_1',
		'cmd /c echo hello world'
	)
	batch_client.task.add('python_test_job', task)

	# Add lots of tasks (up to 100 per call)
	tasks = []
	for i in range(2, 50):
		tasks.append(batch.models.TaskAddParameter(
			'python_task_{}'.format(i),
			'cmd /c echo hello world {}'.format(i))
		)
	batch_client.task.add_collection('python_test_job', tasks)

	# Download task output
	with open('task_output.txt', 'w') as file_output:
		output = batch_client.file.get_from_task(
			'python_test_job',
			'python_task_1',
			'stdout.txt'
		)
		for data in output:
			file_output.write(data)
			
	# Set up a schedule for a recurring job
	job_spec = batch.models.JobSpecification(
		pool_info=batch.models.PoolInformation(pool_id='my_pool')
	)
	schedule = batch.models.Schedule(
		start_window=datetime.timedelta(hours=1),
		recurrance_interval=datetime.timedelta(days=1)
	)
	setup = batch.models.JobScheduleAddParameter(
		'python_test_schedule',
		schedule,
		job_spec
	)
	batch_client.job_schedule.add(setup)

