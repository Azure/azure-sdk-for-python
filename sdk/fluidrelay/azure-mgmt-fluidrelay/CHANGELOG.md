# Release History

## 1.0.0 (2022-08-04)

**Features**

  - Added operation FluidRelayServersOperations.list_keys
  - Added operation group FluidRelayContainersOperations
  - Model FluidRelayEndpoints has a new parameter service_endpoints
  - Model FluidRelayServer has a new parameter encryption
  - Model FluidRelayServer has a new parameter storagesku
  - Model FluidRelayServerUpdate has a new parameter encryption
  - Model FluidRelayServerUpdate has a new parameter location
  - Model Identity has a new parameter user_assigned_identities

**Breaking changes**

  - Operation FluidRelayServersOperations.create_or_update has a new parameter fluid_relay_server_name
  - Operation FluidRelayServersOperations.create_or_update no longer has parameter name
  - Operation FluidRelayServersOperations.delete has a new parameter fluid_relay_server_name
  - Operation FluidRelayServersOperations.delete no longer has parameter name
  - Operation FluidRelayServersOperations.get has a new parameter fluid_relay_server_name
  - Operation FluidRelayServersOperations.get no longer has parameter name
  - Operation FluidRelayServersOperations.regenerate_key has a new parameter fluid_relay_server_name
  - Operation FluidRelayServersOperations.regenerate_key no longer has parameter name
  - Operation FluidRelayServersOperations.update has a new parameter fluid_relay_server_name
  - Operation FluidRelayServersOperations.update no longer has parameter name
  - Removed operation FluidRelayServersOperations.get_keys

## 1.0.0b1 (2021-09-30)

* Initial Release
