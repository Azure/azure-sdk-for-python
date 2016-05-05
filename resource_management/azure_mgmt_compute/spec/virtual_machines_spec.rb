# encoding: utf-8
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.

require_relative 'spec_helper'

include MsRestAzure
include Azure::ARM::Resources
include Azure::ARM::Resources::Models

include Azure::ARM::Compute
include Azure::ARM::Compute::Models

include Azure::ARM::Network
include Azure::ARM::Network::Models

describe 'Virtual machine and vm extension creation' do
  before(:each) do
    @resource_helper = ResourceHelper.new
    @location = 'westus'
    @resource_group = @resource_helper.create_resource_group
    @client = @resource_helper.compute_client.virtual_machines
    @extensions_client = @resource_helper.compute_client.virtual_machine_extensions
  end

  after(:each) do
    @resource_helper.delete_resource_group(@resource_group.name)
  end

  it 'should create virtual machine and vm extension' do
    params = build_virtual_machine_parameters
    vm_name = 'testvm'
    result = @client.create_or_update(@resource_group.name, vm_name, params).value!
    expect(result.response.status).to eq(200)
    expect(result.body).not_to be_nil
    expect(result.body.name).to eq vm_name
    expect(result.body.location).to eq @location

    vm_extension = build_extension_parameter
    ext_name = 'testextension'
    result = @extensions_client.create_or_update(@resource_group.name, vm_name, ext_name, vm_extension).value!
    expect(result.response.status).to eq(200)
    expect(result.body.name).to eq(ext_name)
  end
end

describe 'Virtual machine and vm extension api' do
  before(:each) do
    @resource_helper = ResourceHelper.new
    @client = @resource_helper.compute_client.virtual_machines
    @extensions_client = @resource_helper.compute_client.virtual_machine_extensions
    @resource_group = @resource_helper.create_resource_group
    @location = 'westus'
    @vm_name = 'testvm'
    @client.create_or_update(@resource_group.name, @vm_name, build_virtual_machine_parameters()).value!
    @ext_name = 'testextension'
    @extensions_client.create_or_update(@resource_group.name, @vm_name, @ext_name, build_extension_parameter()).value!
  end

  after(:each) do
    @resource_helper.delete_resource_group(@resource_group.name)
  end

  it 'should get vm extension' do
    result = @extensions_client.get(@resource_group.name, @vm_name, @ext_name, nil).value!
    expect(result.response.status).to eq(200)
    expect(result.body.name).to eq(@ext_name)
  end

  it 'should get vm extension with expand parameter' do
    result = @extensions_client.get(@resource_group.name, @vm_name, @ext_name, 'instanceView').value!
    expect(result.response.status).to eq(200)
    expect(result.body.name).to eq(@ext_name)
  end

  it 'should delete vm extension' do
    result = @extensions_client.delete(@resource_group.name, @vm_name, @ext_name).value!
    expect(result.response.status).to eq(200)
  end
end

describe 'Virtual machine api' do
  before(:each) do
    @resource_helper = ResourceHelper.new
    @client = @resource_helper.compute_client.virtual_machines
    @resource_group = @resource_helper.create_resource_group
    @location = 'westus'
    @vm_name = 'testvm'
    @client.create_or_update(@resource_group.name, @vm_name, build_virtual_machine_parameters()).value!
  end

  after(:each) do
    @resource_helper.delete_resource_group(@resource_group.name)
  end

  it 'should get virtual machine' do
    result = @client.get(@resource_group.name, @vm_name).value!
    expect(result.response.status).to eq(200)
    expect(result.body.name).to eq(@vm_name)
  end

  it 'should get virtual machine with expand parameter' do
    result = @client.get(@resource_group.name, @vm_name, 'instanceView').value!
    expect(result.response.status).to eq(200)
    expect(result.body.name).to eq(@vm_name)
  end

  it 'should list virtual machines' do
    result = @client.list(@resource_group.name).value!
    expect(result.response.status).to eq(200)
    expect(result.body.value).not_to be_nil
    expect(result.body.value).to be_a(Array)
  end

  it 'should list all virtual machines' do
    result = @client.list_all.value!
    expect(result.response.status).to eq(200)
    expect(result.body.value).not_to be_nil
    expect(result.body.value).to be_a(Array)
  end

  it 'should list available sizes' do
    result = @client.list_available_sizes(@resource_group.name, @vm_name).value!
    expect(result.response.status).to eq(200)
    expect(result.body.value).not_to be_nil
    expect(result.body.value).to be_a(Array)
  end

  it 'should restart virtual machine' do
    result = @client.restart(@resource_group.name, @vm_name).value!
    expect(result.response.status).to eq(200)
  end

  it 'should power off virtual machine' do
    result = @client.power_off(@resource_group.name, @vm_name).value!
    expect(result.response.status).to eq(200)
  end

  it 'should start virtual machine' do
    result = @client.start(@resource_group.name, @vm_name).value!
    expect(result.response.status).to eq(200)
  end

  it 'should generalize and capture virtual machine' do
    @client.power_off(@resource_group.name, @vm_name).value!

    # To generalize VM it should be started. But sometimes even after API method
    # starts it - the API still says that it cannot be generalized because it is
    # turned off. Also there is no property provided by API which can be polled
    # to find out whether VM is turned on or not. So the timeout is added here.
    # todo: add VM polling until VM is started if API method appear which provides
    # such info.
    sleep ENV.fetch('RETRY_TIMEOUT', 300).to_i

    result = @client.generalize(@resource_group.name, @vm_name).value!
    expect(result.response.status).to eq(200)

    #capturing VM requires VM to be generalized
    capture_params = VirtualMachineCaptureParameters.new
    capture_params.vhd_prefix = 'test'
    capture_params.destination_container_name = 'test'
    capture_params.overwrite_vhds = true

    result = @client.capture(@resource_group.name, @vm_name, capture_params).value!
    expect(result.response.status).to eq(200)
  end

  it 'should deallocate virtual machine' do
    result = @client.deallocate(@resource_group.name, @vm_name).value!
    expect(result.response.status).to eq(200)
  end

  it 'should delete virtual machine' do
    result = @client.delete(@resource_group.name, @vm_name).value!
    expect(result.response.status).to eq(200)
  end
end

# VM helpers
def build_virtual_machine_parameters
  props = VirtualMachineProperties.new

  windows_config = WindowsConfiguration.new
  windows_config.provision_vmagent = true
  windows_config.enable_automatic_updates = true

  os_profile = OSProfile.new
  os_profile.computer_name = 'testvm1'
  os_profile.admin_username = 'testvm1'
  os_profile.admin_password = 'P@ssword1'
  os_profile.windows_configuration = windows_config
  os_profile.secrets = []
  props.os_profile = os_profile

  hardware_profile = HardwareProfile.new
  hardware_profile.vm_size = 'Standard_A0'
  props.hardware_profile = hardware_profile

  props.storage_profile = create_storage_profile

  props.network_profile = create_network_profile

  params = VirtualMachine.new
  params.type = 'Microsoft.Compute/virtualMachines'
  params.properties = props
  params.location = @location
  params
end

def build_extension_parameter
  vm_extension_properties = VirtualMachineExtensionProperties.new
  vm_extension_properties.publisher = 'Microsoft.Compute'
  vm_extension_properties.type = 'VMAccessAgent'
  vm_extension_properties.type_handler_version = '2.0'
  vm_extension_properties.auto_upgrade_minor_version = true

  vm_extension = VirtualMachineExtension.new
  vm_extension.properties = vm_extension_properties
  vm_extension.tags = Hash.new
  vm_extension.tags['extensionTag1'] = '1'
  vm_extension.tags['extensionTag2'] = '2'
  vm_extension.location = 'westus'
  vm_extension
end

def generate_os_vhd_uri(storage_name)
  container_name = 'testcontainer'
  vhd_container = "https://#{storage_name}.blob.core.windows.net/#{container_name}"
  os_vhduri = "#{vhd_container}/os#{'test'}.vhd"
  os_vhduri
end

def get_image_reference
  ref = ImageReference.new
  ref.publisher = 'MicrosoftWindowsServer'
  ref.offer = 'WindowsServer'
  ref.sku = '2012-R2-Datacenter'
  ref.version = 'latest'
  ref
end

# Storage helpers
def build_storage_account_create_parameters(name)
  params = Azure::ARM::Storage::Models::StorageAccountCreateParameters.new
  params.location = @location
  props = Azure::ARM::Storage::Models::StorageAccountPropertiesCreateParameters.new
  params.properties = props
  props.account_type = 'Standard_GRS'
  params
end

def create_storage_account
  storage_name = 'teststorage53464'
  params = build_storage_account_create_parameters storage_name
  result = @resource_helper.storage_client.storage_accounts.create(@resource_group.name, storage_name, params).value!.body
  result.name = storage_name #similar problem in dot net tests
  result
end

def create_storage_profile
  storage_profile = StorageProfile.new
  storage_profile.image_reference = get_image_reference
  storage = create_storage_account
  os_disk = OSDisk.new
  os_disk.caching = 'None'
  os_disk.create_option = 'fromImage'
  os_disk.name = 'Test'
  virtual_hard_disk = VirtualHardDisk.new
  virtual_hard_disk.uri = generate_os_vhd_uri storage.name
  os_disk.vhd = virtual_hard_disk
  storage_profile.os_disk = os_disk
  storage_profile
end

# Network helpers
def build_public_ip_params(location)
  public_ip = PublicIPAddress.new
  public_ip.location = location
  props = PublicIPAddressPropertiesFormat.new
  props.public_ipallocation_method = 'Dynamic'
  public_ip.properties = props
  domain_name = 'testdomain53464'
  dns_settings = PublicIPAddressDnsSettings.new
  dns_settings.domain_name_label = domain_name
  props.dns_settings = dns_settings
  public_ip
end

def create_public_ip_address(location, resource_group)
  public_ip_address_name = 'test_ip_name'
  params = build_public_ip_params(location)
  @resource_helper.network_client.public_ipaddresses.create_or_update(resource_group.name, public_ip_address_name, params).value!.body
end

def build_virtual_network_params(location)
  params = VirtualNetwork.new
  props = VirtualNetworkPropertiesFormat.new
  params.location = location
  address_space = AddressSpace.new
  address_space.address_prefixes = ['10.0.0.0/16']
  props.address_space = address_space
  dhcp_options = DhcpOptions.new
  dhcp_options.dns_servers = %w(10.1.1.1 10.1.2.4)
  props.dhcp_options = dhcp_options
  sub2 = Subnet.new
  sub2_prop = SubnetPropertiesFormat.new
  sub2.name = 'subnet253464'
  sub2_prop.address_prefix = '10.0.2.0/24'
  sub2.properties = sub2_prop
  props.subnets = [sub2]
  params.properties = props
  params
end

def create_virtual_network(resource_group_name)
  virtualNetworkName = "testvnet53464"
  params = build_virtual_network_params('westus')
  @resource_helper.network_client.virtual_networks.create_or_update(resource_group_name, virtualNetworkName, params).value!.body
end

def build_subnet_params
  params = Subnet.new
  prop = SubnetPropertiesFormat.new
  params.properties = prop
  prop.address_prefix = '10.0.1.0/24'
  params
end

def create_subnet(virtual_network, resource_group, subnet_client)
  subnet_name = 'testsubnet53464'
  params = build_subnet_params

  subnet_client.create_or_update(resource_group.name, virtual_network.name, subnet_name, params).value!.body
end

def create_network_interface
  params = build_network_interface_param
  @resource_helper.network_client.network_interfaces.create_or_update(@resource_group.name, params.name, params).value!.body
end

def build_network_interface_param
  params = NetworkInterface.new
  params.location = @location
  network_interface_name = 'testnic53464'
  ip_config_name = 'ip_name53464'
  params.name = network_interface_name
  props = NetworkInterfacePropertiesFormat.new
  ip_configuration = NetworkInterfaceIPConfiguration.new
  params.properties = props
  props.ip_configurations = [ip_configuration]
  ip_configuration_properties = NetworkInterfaceIPConfigurationPropertiesFormat.new
  ip_configuration.properties = ip_configuration_properties
  ip_configuration.name = ip_config_name
  ip_configuration_properties.private_ipallocation_method = 'Dynamic'
  ip_configuration_properties.public_ipaddress = create_public_ip_address(@location, @resource_group)
  ip_configuration_properties.subnet = @subnet
  params
end

def create_network_profile
  vn = create_virtual_network(@resource_group.name)
  @subnet = create_subnet(vn, @resource_group, @resource_helper.network_client.subnets)
  network_interface = create_network_interface

  profile = NetworkProfile.new
  profile.network_interfaces = [network_interface]

  profile
end
