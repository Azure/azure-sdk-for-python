# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import TYPE_CHECKING, List, Any
from urllib.parse import urlparse

from azure.core.tracing.decorator import distributed_trace
from azure.core.paging import ItemPaged

from ._models import SipDomain, SipTrunk, SipTrunkRoute
from ._mappers import (
    sip_trunk_from_generated,
    sip_trunk_to_generated,
    sip_trunk_route_from_generated,
    sip_trunk_route_to_generated,
    sip_domain_from_generated,
    sip_domain_to_generated
)
from ._generated.models import ExpandEnum, SipConfiguration
from ._generated._client import SIPRoutingService
from .._shared.auth_policy_utils import get_authentication_policy
from .._shared.utils import parse_connection_str
from .._version import SDK_MONIKER

if TYPE_CHECKING:
    from azure.core.credentials import TokenCredential


class SipRoutingClient(object):
    """A client to interact with the AzureCommunicationService SIP routing gateway.
    This client provides operations to retrieve and manage SIP routing configuration.

    :param endpoint: The endpoint url for Azure Communication Service resource.
    :type endpoint: str
    :param credential: The credentials with which to authenticate.
    :type credential: TokenCredential
    :keyword api_version: Api Version. Default value is "2021-05-01-preview". Note that overriding
     this default value may result in unsupported behavior.
    :paramtype api_version: str
    """
    def __init__(
        self,
        endpoint: str,
        credential: "TokenCredential",
        **kwargs: Any
    )-> "SipRoutingClient":

        if not credential:
            raise ValueError("credential can not be None")
        try:
            if not endpoint.lower().startswith("http"):
                endpoint = "https://" + endpoint
        except AttributeError:
            raise ValueError("Host URL must be a string")  # pylint:disable=raise-missing-from

        parsed_url = urlparse(endpoint.rstrip("/"))
        if not parsed_url.netloc:
            raise ValueError("Invalid URL: {}".format(endpoint))

        self._endpoint = endpoint
        self._authentication_policy = get_authentication_policy(endpoint, credential)

        self._rest_service = SIPRoutingService(
            self._endpoint, credential=credential, authentication_policy=self._authentication_policy,
            sdk_moniker=SDK_MONIKER, **kwargs
        )

    @classmethod
    def from_connection_string(
        cls,
        conn_str: str,
        **kwargs: Any
    ) -> "SipRoutingClient":
        """Factory method for creating client from connection string.

        :param str conn_str: Connection string containing endpoint and credentials.
        :returns: The newly created client.
        :rtype: ~azure.communication.siprouting.SipRoutingClient
        """
        endpoint, credential = parse_connection_str(conn_str)
        return cls(endpoint, credential, **kwargs)

    @distributed_trace
    def get_trunk(
        self,
        trunk_fqdn: str,
        **kwargs: Any
    ) -> SipTrunk:
        """Retrieve a single SIP trunk.

        :param trunk_fqdn: FQDN of the desired SIP trunk.
        :type trunk_fqdn: str
        :returns: SIP trunk with specified trunk_fqdn. If it doesn't exist, throws KeyError.
        :rtype: ~azure.communication.siprouting.models.SipTrunk
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError, KeyError
        """
        if trunk_fqdn is None:
            raise ValueError("Parameter 'trunk_fqdn' must not be None.")

        config = self._rest_service.sip_routing.get(expand = ExpandEnum.TRUNKS_HEALTH, **kwargs)

        trunk = config.trunks[trunk_fqdn]
        return sip_trunk_from_generated(trunk_fqdn, trunk)

    @distributed_trace
    def set_trunk(
        self,
        trunk: SipTrunk,
        **kwargs: Any
    ) -> None:
        """Modifies SIP trunk with the given FQDN. If it doesn't exist, adds a new trunk.

        :param trunk: Trunk object to be set.
        :type trunk: ~azure.communication.siprouting.models.SipTrunk
        :returns: None
        :rtype: None
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError
        """
        if trunk is None:
            raise ValueError("Parameter 'trunk' must not be None.")

        self._update_trunks_([trunk], **kwargs)

    @distributed_trace
    def delete_trunk(
        self,
        trunk_fqdn: str,
        **kwargs: Any
    ) -> None:
        """Deletes SIP trunk.

        :param trunk_fqdn: FQDN of the trunk to be deleted.
        :type trunk_fqdn: str
        :returns: None
        :rtype: None
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError
        """
        if trunk_fqdn is None:
            raise ValueError("Parameter 'trunk_fqdn' must not be None.")

        self._rest_service.sip_routing.update(body=SipConfiguration(trunks={trunk_fqdn: None}), **kwargs)

    @distributed_trace
    def list_trunks(
        self,
        **kwargs: Any
    ) -> ItemPaged[SipTrunk]:
        """Retrieves the currently configured SIP trunks.
        
        :returns: Current SIP trunks configuration.
        :rtype: ItemPaged[~azure.communication.siprouting.models.SipTrunk]
        :raises: ~azure.core.exceptions.HttpResponseError
        """

        def extract_data(config):
            list_of_elem = [sip_trunk_from_generated(k,v) for k, v in config.trunks.items()]
            return None, list_of_elem

        # pylint: disable=unused-argument
        def get_next(nextLink=None):
            return self._rest_service.sip_routing.get(expand=ExpandEnum.TRUNKS_HEALTH, **kwargs)

        return ItemPaged(get_next, extract_data)

    @distributed_trace
    def list_routes(
        self,
        **kwargs: Any
    ) -> ItemPaged[SipTrunkRoute]:
        """Retrieves the currently configured SIP routes.

        :returns: Current SIP routes configuration.
        :rtype: ItemPaged[~azure.communication.siprouting.models.SipTrunkRoute]
        :raises: ~azure.core.exceptions.HttpResponseError
        """

        def extract_data(config):
            list_of_elem = [sip_trunk_route_from_generated(x) for x in config.routes]
            return None, list_of_elem

        # pylint: disable=unused-argument
        def get_next(nextLink=None):
            return self._rest_service.sip_routing.get(**kwargs)

        return ItemPaged(get_next, extract_data)

    @distributed_trace
    def set_trunks(
        self,
        trunks: List[SipTrunk],
        **kwargs: Any
    ) -> None:
        """Overwrites the list of SIP trunks.

        :param trunks: New list of trunks to be set.
        :type trunks: List[SipTrunk]
        :returns: None
        :rtype: None
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError
        """
        if trunks is None:
            raise ValueError("Parameter 'trunks' must not be None.")

        trunks_dictionary = {x.fqdn: sip_trunk_to_generated(x) for x in trunks}
        config = SipConfiguration(trunks=trunks_dictionary)

        old_trunks = self._list_trunks_(**kwargs)

        for x in old_trunks:
            if x.fqdn not in [o.fqdn for o in trunks]:
                config.trunks[x.fqdn] = None

        if len(config.trunks) > 0:
            self._rest_service.sip_routing.update(body=config, **kwargs)

    @distributed_trace
    def set_routes(
        self,
        routes: List[SipTrunkRoute],
        **kwargs: Any
    ) -> None:
        """Overwrites the list of SIP routes.

        :param routes: New list of routes to be set.
        :type routes: List[SipTrunkRoute]
        :returns: None
        :rtype: None
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError
        """
        if routes is None:
            raise ValueError("Parameter 'routes' must not be None.")

        routes_internal = [sip_trunk_route_to_generated(x) for x in routes]
        self._rest_service.sip_routing.update(body=SipConfiguration(routes=routes_internal), **kwargs)

    @distributed_trace
    def get_routes_for_number(
       self,
        target_phone_number: str,
        test_routes: List[SipTrunkRoute],
        **kwargs: Any
    ) -> List[SipTrunkRoute]:
        """Gets the list of routes matching the target phone number, ordered by priority.

        Gets the list of routes matching the target phone number, ordered by priority.

        :param target_phone_number: Phone number to test routing patterns against. Required.
        :type target_phone_number: str
        :param test_routes: New list of routes to be set.
        :type test_routes: List[SipTrunkRoute]
        :return: List of routes matching the sip trunk route,
         provided in the same order of priority as in SipConfiguration.
        :rtype: List[SipTrunkRoute]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        if test_routes is None:
            raise ValueError("Parameter 'test_routes' must not be None.")

        routes_internal = [sip_trunk_route_to_generated(x) for x in test_routes]
        sip_configuration = SipConfiguration(routes=routes_internal)
        response = self._rest_service.sip_routing.test_routes_with_number(sip_configuration=sip_configuration,
                                                                      target_phone_number=target_phone_number,
                                                                      **kwargs)
        routes_mapped = [sip_trunk_route_from_generated(x) for x in response.matching_routes]
        return routes_mapped

    @distributed_trace
    def get_domain(
        self,
        domain_name: str,
        **kwargs: Any
    ) -> SipDomain:
        """Retrieve a single SIP domain.

        :param domain_name: domain_name of the desired SIP Domain.
        :type domain_name: str
        :returns: SIP Domain with specified domain_name. If it doesn't exist, throws KeyError.
        :rtype: ~azure.communication.siprouting.models.SipDomain
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError, KeyError
        """
        if domain_name is None:
            raise ValueError("Parameter 'domain_name' must not be None.")
        config = self._rest_service.sip_routing.get( **kwargs)

        domain = config.domains[domain_name]
        return sip_domain_from_generated(domain_name,domain)

    @distributed_trace
    def set_domain(
        self,
        domain: SipDomain,
        **kwargs: Any
    ) -> None:
        """Modifies SIP domain with the given domain. If it doesn't exist, adds a new domain.

        :param domain: Domain object to be set.
        :type domain: ~azure.communication.siprouting.models.SipDomain
        :returns: None
        :rtype: None
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError
        """
        if domain is None:
            raise ValueError("Parameter 'domain' must not be None.")

        self._update_domains_([domain], **kwargs)

    @distributed_trace
    def delete_domain(
        self,
        domain_name: str,
        **kwargs: Any
    ) -> None:
        """Deletes SIP Domain.

        :param domain_name: domain_name of the Domain to be deleted.
        :type domain_name: str
        :returns: None
        :rtype: None
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError
        """
        if domain_name is None:
            raise ValueError("Parameter 'domain_name' must not be None.")

        self._rest_service.sip_routing.update(body=SipConfiguration(domains={domain_name: None}), **kwargs)

    @distributed_trace
    def list_domains(
        self,
        **kwargs: Any
    ) -> ItemPaged[SipDomain]:
        """Retrieves the currently configured SIP Domain.
        
        :returns: Current SIP domains configuration.
        :rtype: ItemPaged[~azure.communication.siprouting.models.SipDomain]
        :raises: ~azure.core.exceptions.HttpResponseError
        """

        def extract_data(config):
            list_of_elem = [sip_domain_from_generated(k,v) for k, v in config.domains.items()]
            return None, list_of_elem

        # pylint: disable=unused-argument
        def get_next(nextLink=None):
            return self._rest_service.sip_routing.get(**kwargs)

        return ItemPaged(get_next, extract_data)

    @distributed_trace
    def set_domains(
        self,
        domains: List[SipDomain],
        **kwargs: Any
    ) -> None:
        """Overwrites the list of SIP domains.

        :param domains: New list of domains to be set.
        :type domains: List[SipDomain]
        :returns: None
        :rtype: None
        :raises: ~azure.core.exceptions.HttpResponseError, ValueError
        """
        if domains is None:
            raise ValueError("Parameter 'domains' must not be None.")

        domains_dictionary = {x.fqdn: sip_domain_to_generated(x) for x in domains}
        config = SipConfiguration(domains=domains_dictionary)

        old_domains = self._list_domains_(**kwargs)

        for x in old_domains:
            if x.fqdn not in [o.fqdn for o in domains]:
                config.domains[x.fqdn] = None

        if len(config.domains) > 0:
            self._rest_service.sip_routing.update(body=config, **kwargs)

    def _list_trunks_(self, **kwargs: Any) -> List[SipTrunk]:
        config = self._rest_service.sip_routing.get(**kwargs)
        return [sip_trunk_from_generated(k,v) for k, v in config.trunks.items()]

    def _list_domains_(self, **kwargs):
        config = self._rest_service.sip_routing.get(**kwargs)
        return [sip_domain_from_generated(k,v) for k, v in config.domains.items()]

    def _update_trunks_(
        self,
        trunks: List[SipTrunk],
        **kwargs: Any
    ) -> List[SipTrunk]:
        modified_config = SipConfiguration(trunks=trunks_internal)

        new_config = self._rest_service.sip_routing.update(body=modified_config, **kwargs)
        return [sip_trunk_from_generated(k,v) for k, v in new_config.trunks.items()]

    def _update_domains_(
        self,
        domains: List[SipDomain],
        **kwargs: Any
    )-> SipDomain:
        domains_internal = {x.fqdn: sip_domain_to_generated(x) for x in domains}
        modified_config = SipConfiguration(domains=domains_internal)

        new_config = self._rest_service.sip_routing.update(body=modified_config, **kwargs)
        return [sip_domain_from_generated(k,v) for k, v in new_config.domains.items()]

    def close(self) -> None:
        self._rest_service.close()

    def __enter__(self) -> "SipRoutingClient":
        self._rest_service.__enter__()
        return self

    def __exit__(self, *args) -> None:
        self._rest_service.__exit__(*args)
