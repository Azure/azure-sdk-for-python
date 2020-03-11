#-------------------------------------------------------------------------
# Copyright (c) Microsoft.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#--------------------------------------------------------------------------
import json
import sys
from datetime import datetime
from xml.dom import minidom
from ._common_models import (
    Feed,
    WindowsAzureData,
    _Base64String,
    _dict_of,
    _list_of,
    _scalar_list_of,
    _strtype,
    _unicode_type,
    _xml_attribute,
)
from ._common_conversion import (
    _decode_base64_to_text,
    _encode_base64,
    _lower,
    _str,
    _decode_base64_to_bytes,
)
from ._common_serialization import (
    _create_entry,
    _get_serialization_name,
    _set_continuation_from_response_headers,
    _get_readable_id,
)
from ._common_error import (
    _general_error_handler,
    _validate_not_none,
)
from .models import (
    AvailabilityResponse,
    CreateServerResponse,
    LinuxConfigurationSet,
    ServiceBusNamespace,
    ServiceBusRegion,
    WindowsConfigurationSet,
)

METADATA_NS = 'http://schemas.microsoft.com/ado/2007/08/dataservices/metadata'

class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        else:
            return super(JSONEncoder, self).default(obj)


class _MinidomXmlToObject(object):

    @staticmethod
    def parse_response(response, return_type):
        '''
        Parse the HTTPResponse's body and fill all the data into a class of
        return_type.
        '''
        doc = minidom.parseString(response.body)
        return_obj = return_type()
        xml_name = return_type._xml_name if hasattr(return_type, '_xml_name') else return_type.__name__ 
        for node in _MinidomXmlToObject.get_child_nodes(doc, xml_name):
            _MinidomXmlToObject._fill_data_to_return_object(node, return_obj)

        return return_obj


    @staticmethod
    def parse_service_resources_response(response, return_type):
        '''
        Parse the HTTPResponse's body and fill all the data into a class of
        return_type.
        '''
        doc = minidom.parseString(response.body)
        return_obj = _list_of(return_type)
        for node in _MinidomXmlToObject.get_children_from_path(doc, "ServiceResources", "ServiceResource"):
            local_obj = return_type()
            _MinidomXmlToObject._fill_data_to_return_object(node, local_obj)
            return_obj.append(local_obj)

        return return_obj


    @staticmethod
    def fill_data_member(xmldoc, element_name, data_member):
        xmlelements = _MinidomXmlToObject.get_child_nodes(
            xmldoc, _get_serialization_name(element_name))

        if not xmlelements or not xmlelements[0].childNodes:
            return None

        value = xmlelements[0].firstChild.nodeValue

        if data_member is None:
            return value
        elif isinstance(data_member, datetime):
            return _to_datetime(value)
        elif type(data_member) is bool:
            return value.lower() != 'false'
        else:
            return type(data_member)(value)


    @staticmethod
    def convert_xml_to_azure_object(xmlstr, azure_type, include_id=True, use_title_as_id=True):
        xmldoc = minidom.parseString(xmlstr)
        return_obj = azure_type()
        xml_name = azure_type._xml_name if hasattr(azure_type, '_xml_name') else azure_type.__name__

        # Only one entry here
        for xml_entry in _MinidomXmlToObject.get_children_from_path(xmldoc,
                                                 'entry'):
            for node in _MinidomXmlToObject.get_children_from_path(xml_entry,
                                                'content',
                                                xml_name):
                _MinidomXmlToObject._fill_data_to_return_object(node, return_obj)
            for name, value in _MinidomXmlToObject.get_entry_properties_from_node(
                xml_entry,
                include_id=include_id,
                use_title_as_id=use_title_as_id).items():
                setattr(return_obj, name, value)
        return return_obj


    @staticmethod
    def get_entry_properties_from_node(entry, include_id, id_prefix_to_skip=None, use_title_as_id=False):
        ''' get properties from entry xml '''
        properties = {}

        etag = entry.getAttributeNS(METADATA_NS, 'etag')
        if etag:
            properties['etag'] = etag
        for updated in _MinidomXmlToObject.get_child_nodes(entry, 'updated'):
            properties['updated'] = updated.firstChild.nodeValue
        for name in _MinidomXmlToObject.get_children_from_path(entry, 'author', 'name'):
            if name.firstChild is not None:
                properties['author'] = name.firstChild.nodeValue

        if include_id:
            if use_title_as_id:
                for title in _MinidomXmlToObject.get_child_nodes(entry, 'title'):
                    properties['name'] = title.firstChild.nodeValue
            else:
                # TODO: check if this is used
                for id in _MinidomXmlToObject.get_child_nodes(entry, 'id'):
                    properties['name'] = _get_readable_id(
                        id.firstChild.nodeValue, id_prefix_to_skip)

        return properties


    @staticmethod
    def convert_response_to_feeds(response, convert_func):
        if response is None:
            return None

        feeds = _list_of(Feed)

        _set_continuation_from_response_headers(feeds, response)

        xmldoc = minidom.parseString(response.body)
        xml_entries = _MinidomXmlToObject.get_children_from_path(xmldoc, 'feed', 'entry')
        if not xml_entries:
            # in some cases, response contains only entry but no feed
            xml_entries = _MinidomXmlToObject.get_children_from_path(xmldoc, 'entry')
        for xml_entry in xml_entries:
            new_node = _MinidomXmlToObject._clone_node_with_namespaces(xml_entry, xmldoc)
            feeds.append(convert_func(new_node.toxml('utf-8')))

        return feeds


    @staticmethod
    def get_first_child_node_value(parent_node, node_name):
        xml_attrs = _MinidomXmlToObject.get_child_nodes(parent_node, node_name)
        if xml_attrs:
            xml_attr = xml_attrs[0]
            if xml_attr.firstChild:
                value = xml_attr.firstChild.nodeValue
                return value


    @staticmethod
    def get_children_from_path(node, *path):
        '''descends through a hierarchy of nodes returning the list of children
        at the inner most level.  Only returns children who share a common parent,
        not cousins.'''
        cur = node
        for index, child in enumerate(path):
            if isinstance(child, _strtype):
                next = _MinidomXmlToObject.get_child_nodes(cur, child)
            else:
                next = _MinidomXmlToObject._get_child_nodesNS(cur, *child)
            if index == len(path) - 1:
                return next
            elif not next:
                break

            cur = next[0]
        return []


    @staticmethod
    def get_child_nodes(node, tagName):
        if ':' not in tagName:
            return _MinidomXmlToObject._get_child_nodesNS(node, '*', tagName)
        else:
            return [childNode for childNode in node.getElementsByTagName(tagName)
                    if childNode.parentNode == node]

    @staticmethod
    def _get_child_nodesNS(node, ns, tagName):
        return [childNode for childNode in node.getElementsByTagNameNS(ns, tagName)
                if childNode.parentNode == node]


    @staticmethod
    def _parse_response_body_from_xml_node(node, return_type):
        '''
        parse the xml and fill all the data into a class of return_type
        '''
        return_obj = return_type()
        _MinidomXmlToObject._fill_data_to_return_object(node, return_obj)

        return return_obj


    @staticmethod
    def _fill_list_of(xmldoc, element_type, xml_element_name):
        xmlelements = _MinidomXmlToObject.get_child_nodes(xmldoc, xml_element_name)
        return [_MinidomXmlToObject._parse_response_body_from_xml_node(xmlelement, element_type) \
            for xmlelement in xmlelements]


    @staticmethod
    def _fill_scalar_list_of(xmldoc, element_type, parent_xml_element_name,
                             xml_element_name):
        '''Converts an xml fragment into a list of scalar types.  The parent xml
        element contains a flat list of xml elements which are converted into the
        specified scalar type and added to the list.
        Example:
        xmldoc=
    <Endpoints>
        <Endpoint>http://{storage-service-name}.blob.core.windows.net/</Endpoint>
        <Endpoint>http://{storage-service-name}.queue.core.windows.net/</Endpoint>
        <Endpoint>http://{storage-service-name}.table.core.windows.net/</Endpoint>
    </Endpoints>
        element_type=str
        parent_xml_element_name='Endpoints'
        xml_element_name='Endpoint'
        '''
        xmlelements = _MinidomXmlToObject.get_child_nodes(xmldoc, parent_xml_element_name)
        if xmlelements:
            xmlelements = _MinidomXmlToObject.get_child_nodes(xmlelements[0], xml_element_name)
            return [_MinidomXmlToObject._get_node_value(xmlelement, element_type) \
                for xmlelement in xmlelements]


    @staticmethod
    def _fill_dict(xmldoc, element_name):
        xmlelements = _MinidomXmlToObject.get_child_nodes(xmldoc, element_name)
        if xmlelements:
            return_obj = {}
            for child in xmlelements[0].childNodes:
                if child.firstChild:
                    return_obj[child.nodeName] = child.firstChild.nodeValue
            return return_obj


    @staticmethod
    def _fill_dict_of(xmldoc, parent_xml_element_name, pair_xml_element_name,
                      key_xml_element_name, value_xml_element_name):
        '''Converts an xml fragment into a dictionary. The parent xml element
        contains a list of xml elements where each element has a child element for
        the key, and another for the value.
        Example:
        xmldoc=
    <ExtendedProperties>
        <ExtendedProperty>
            <Name>Ext1</Name>
            <Value>Val1</Value>
        </ExtendedProperty>
        <ExtendedProperty>
            <Name>Ext2</Name>
            <Value>Val2</Value>
        </ExtendedProperty>
    </ExtendedProperties>
        element_type=str
        parent_xml_element_name='ExtendedProperties'
        pair_xml_element_name='ExtendedProperty'
        key_xml_element_name='Name'
        value_xml_element_name='Value'
        '''
        return_obj = {}

        xmlelements = _MinidomXmlToObject.get_child_nodes(xmldoc, parent_xml_element_name)
        if xmlelements:
            xmlelements = _MinidomXmlToObject.get_child_nodes(xmlelements[0], pair_xml_element_name)
            for pair in xmlelements:
                keys = _MinidomXmlToObject.get_child_nodes(pair, key_xml_element_name)
                values = _MinidomXmlToObject.get_child_nodes(pair, value_xml_element_name)
                if keys and values:
                    key = keys[0].firstChild.nodeValue
                    valueContentNode = values[0].firstChild
                    value = valueContentNode.nodeValue if valueContentNode else None
                    return_obj[key] = value

        return return_obj


    @staticmethod
    def _fill_instance_child(xmldoc, element_name, return_type):
        '''Converts a child of the current dom element to the specified type.
        '''
        xmlelements = _MinidomXmlToObject.get_child_nodes(
            xmldoc, _get_serialization_name(element_name))

        if not xmlelements:
            return None

        return_obj = return_type()
        _MinidomXmlToObject._fill_data_to_return_object(xmlelements[0], return_obj)

        return return_obj


    @staticmethod
    def _get_node_value(xmlelement, data_type):
        value = xmlelement.firstChild.nodeValue
        if data_type is datetime:
            return _to_datetime(value)
        elif data_type is bool:
            return value.lower() != 'false'
        else:
            return data_type(value)


    @staticmethod
    def _fill_data_to_return_object(node, return_obj):
        members = dict(vars(return_obj))
        for name, value in members.items():
            if isinstance(value, _list_of):
                setattr(return_obj,
                        name,
                        _MinidomXmlToObject._fill_list_of(
                            node,
                            value.list_type,
                            value.xml_element_name))
            elif isinstance(value, _scalar_list_of):
                setattr(return_obj,
                        name,
                        _MinidomXmlToObject._fill_scalar_list_of(
                            node,
                            value.list_type,
                            _get_serialization_name(name),
                            value.xml_element_name))
            elif isinstance(value, _dict_of):
                setattr(return_obj,
                        name,
                        _MinidomXmlToObject._fill_dict_of(
                            node,
                            _get_serialization_name(name),
                            value.pair_xml_element_name,
                            value.key_xml_element_name,
                            value.value_xml_element_name))
            elif isinstance(value, _xml_attribute):
                real_value = None
                if node.hasAttribute(value.xml_element_name):
                    real_value = node.getAttribute(value.xml_element_name)
                if real_value is not None:
                    setattr(return_obj, name, real_value)
            elif isinstance(value, WindowsAzureData):
                setattr(return_obj,
                        name,
                        _MinidomXmlToObject._fill_instance_child(
                            node,
                            name,
                            value.__class__))
            elif isinstance(value, dict):
                setattr(return_obj,
                        name,
                        _MinidomXmlToObject._fill_dict(
                            node,
                            _get_serialization_name(name)))
            elif isinstance(value, _Base64String):
                value = _MinidomXmlToObject.fill_data_member(
                    node,
                    name,
                    '')
                if value is not None:
                    value = _decode_base64_to_text(value)
                # always set the attribute, so we don't end up returning an object
                # with type _Base64String
                setattr(return_obj, name, value)
            else:
                value = _MinidomXmlToObject.fill_data_member(
                    node,
                    name,
                    value)
                if value is not None:
                    setattr(return_obj, name, value)


    @staticmethod
    def _find_namespaces_from_child(parent, child, namespaces):
        """Recursively searches from the parent to the child,
        gathering all the applicable namespaces along the way"""
        for cur_child in parent.childNodes:
            if cur_child is child:
                return True
            if _MinidomXmlToObject._find_namespaces_from_child(cur_child, child, namespaces):
                # we are the parent node
                for key in cur_child.attributes.keys():
                    if key.startswith('xmlns:') or key == 'xmlns':
                        namespaces[key] = cur_child.attributes[key]
                break
        return False


    @staticmethod
    def _find_namespaces(parent, child):
        res = {}
        for key in parent.documentElement.attributes.keys():
            if key.startswith('xmlns:') or key == 'xmlns':
                res[key] = parent.documentElement.attributes[key]
        _MinidomXmlToObject._find_namespaces_from_child(parent, child, res)
        return res


    @staticmethod
    def _clone_node_with_namespaces(node_to_clone, original_doc):
        clone = node_to_clone.cloneNode(True)

        for key, value in _MinidomXmlToObject._find_namespaces(original_doc, node_to_clone).items():
            clone.attributes[key] = value

        return clone


def _data_to_xml(data):
    '''Creates an xml fragment from the specified data.
        data:
            Array of tuples, where first: xml element name
                                    second:
                                        xml element text
                                    third:
                                        conversion function
    '''
    xml = ''
    for element in data:
        name = element[0]
        val = element[1]
        if len(element) > 2:
            converter = element[2]
        else:
            converter = None

        if val is not None:
            if converter is not None:
                text = _str(converter(_str(val)))
            else:
                text = _str(val)

            xml += ''.join(['<', name, '>', text, '</', name, '>'])
    return xml


class _XmlSerializer(object):

    @staticmethod
    def create_storage_service_input_to_xml(service_name, description, label,
                                            affinity_group, location,
                                            account_type,
                                            extended_properties):
        xml = _XmlSerializer.data_to_xml(
            [('ServiceName', service_name),
             ('Description', description),
             ('Label', label, _encode_base64),
             ('AffinityGroup', affinity_group),
             ('Location', location)])
        if extended_properties is not None:
            xml += _XmlSerializer.extended_properties_dict_to_xml_fragment(
                extended_properties)
        xml += _XmlSerializer.data_to_xml([('AccountType', account_type)])
        return _XmlSerializer.doc_from_xml('CreateStorageServiceInput', xml)

    @staticmethod
    def update_storage_service_input_to_xml(description, label,
                                            account_type,
                                            extended_properties):
        xml = _XmlSerializer.data_to_xml(
            [('Description', description),
             ('Label', label, _encode_base64)])
        if extended_properties is not None:
            xml += _XmlSerializer.extended_properties_dict_to_xml_fragment(
                extended_properties)
        xml += _XmlSerializer.data_to_xml([('AccountType', account_type)])
        return _XmlSerializer.doc_from_xml('UpdateStorageServiceInput', xml)

    @staticmethod
    def regenerate_keys_to_xml(key_type):
        return _XmlSerializer.doc_from_data('RegenerateKeys',
                                            [('KeyType', key_type)])

    @staticmethod
    def update_hosted_service_to_xml(label, description, extended_properties):
        return _XmlSerializer.doc_from_data('UpdateHostedService',
                                            [('Label', label, _encode_base64),
                                             ('Description', description)],
                                            extended_properties)

    @staticmethod
    def create_hosted_service_to_xml(service_name, label, description,
                                     location, affinity_group,
                                     extended_properties):
        return _XmlSerializer.doc_from_data(
            'CreateHostedService',
            [('ServiceName', service_name),
             ('Label', label, _encode_base64),
             ('Description', description),
             ('Location', location),
             ('AffinityGroup', affinity_group)],
            extended_properties)

    @staticmethod
    def create_deployment_to_xml(name, package_url, label, configuration,
                                 start_deployment, treat_warnings_as_error,
                                 extended_properties):
        return _XmlSerializer.doc_from_data(
            'CreateDeployment',
            [('Name', name),
             ('PackageUrl', package_url),
             ('Label', label, _encode_base64),
             ('Configuration', configuration),
             ('StartDeployment',
             start_deployment, _lower),
             ('TreatWarningsAsError', treat_warnings_as_error, _lower)],
            extended_properties)

    @staticmethod
    def swap_deployment_to_xml(production, source_deployment):
        return _XmlSerializer.doc_from_data(
            'Swap',
            [('Production', production),
             ('SourceDeployment', source_deployment)])

    @staticmethod
    def update_deployment_status_to_xml(status):
        return _XmlSerializer.doc_from_data(
            'UpdateDeploymentStatus',
            [('Status', status)])

    @staticmethod
    def change_deployment_to_xml(configuration, treat_warnings_as_error, mode,
                                 extended_properties):
        return _XmlSerializer.doc_from_data(
            'ChangeConfiguration',
            [('Configuration', configuration),
             ('TreatWarningsAsError', treat_warnings_as_error, _lower),
             ('Mode', mode)],
            extended_properties)

    @staticmethod
    def upgrade_deployment_to_xml(mode, package_url, configuration, label,
                                  role_to_upgrade, force, extended_properties):
        return _XmlSerializer.doc_from_data(
            'UpgradeDeployment',
            [('Mode', mode),
             ('PackageUrl', package_url),
             ('Configuration', configuration),
             ('Label', label, _encode_base64),
             ('RoleToUpgrade', role_to_upgrade),
             ('Force', force, _lower)],
            extended_properties)

    @staticmethod
    def rollback_upgrade_to_xml(mode, force):
        return _XmlSerializer.doc_from_data(
            'RollbackUpdateOrUpgrade',
            [('Mode', mode),
             ('Force', force, _lower)])

    @staticmethod
    def walk_upgrade_domain_to_xml(upgrade_domain):
        return _XmlSerializer.doc_from_data(
            'WalkUpgradeDomain',
            [('UpgradeDomain', upgrade_domain)])

    @staticmethod
    def certificate_file_to_xml(data, certificate_format, password):
        return _XmlSerializer.doc_from_data(
            'CertificateFile',
            [('Data', data),
             ('CertificateFormat', certificate_format),
             ('Password', password)])

    @staticmethod
    def create_affinity_group_to_xml(name, label, description, location):
        return _XmlSerializer.doc_from_data(
            'CreateAffinityGroup',
            [('Name', name),
             ('Label', label, _encode_base64),
             ('Description', description),
             ('Location', location)])

    @staticmethod
    def update_affinity_group_to_xml(label, description):
        return _XmlSerializer.doc_from_data(
            'UpdateAffinityGroup',
            [('Label', label, _encode_base64),
             ('Description', description)])

    @staticmethod
    def subscription_certificate_to_xml(public_key, thumbprint, data):
        return _XmlSerializer.doc_from_data(
            'SubscriptionCertificate',
            [('SubscriptionCertificatePublicKey', public_key),
             ('SubscriptionCertificateThumbprint', thumbprint),
             ('SubscriptionCertificateData', data)])

    @staticmethod
    def os_image_to_xml(label, media_link, name, os):
        return _XmlSerializer.doc_from_data(
            'OSImage',
            [('Label', label),
             ('MediaLink', media_link),
             ('Name', name),
             ('OS', os)])

    @staticmethod
    def data_virtual_hard_disk_to_xml(host_caching, disk_label, disk_name, lun,
                                      logical_disk_size_in_gb, media_link,
                                      source_media_link):
        return _XmlSerializer.doc_from_data(
            'DataVirtualHardDisk',
            [('HostCaching', host_caching),
             ('DiskLabel', disk_label),
             ('DiskName', disk_name),
             ('Lun', lun),
             ('LogicalDiskSizeInGB', logical_disk_size_in_gb),
             ('MediaLink', media_link),
             ('SourceMediaLink', source_media_link)])

    @staticmethod
    def disk_to_xml(label, media_link, name, os):
        return _XmlSerializer.doc_from_data(
            'Disk',
            [('OS', os),
             ('Label', label),
             ('MediaLink', media_link),
             ('Name', name),
             ])

    @staticmethod
    def restart_role_operation_to_xml():
        return _XmlSerializer.doc_from_xml(
            'RestartRoleOperation',
            '<OperationType>RestartRoleOperation</OperationType>')

    @staticmethod
    def shutdown_role_operation_to_xml(post_shutdown_action):
        xml = _XmlSerializer.data_to_xml(
            [('OperationType', 'ShutdownRoleOperation'),
             ('PostShutdownAction', post_shutdown_action)])
        return _XmlSerializer.doc_from_xml('ShutdownRoleOperation', xml)

    @staticmethod
    def shutdown_roles_operation_to_xml(role_names, post_shutdown_action):
        xml = _XmlSerializer.data_to_xml(
            [('OperationType', 'ShutdownRolesOperation')])
        xml += '<Roles>'
        for role_name in role_names:
            xml += _XmlSerializer.data_to_xml([('Name', role_name)])
        xml += '</Roles>'
        xml += _XmlSerializer.data_to_xml(
             [('PostShutdownAction', post_shutdown_action)])
        return _XmlSerializer.doc_from_xml('ShutdownRolesOperation', xml)

    @staticmethod
    def start_role_operation_to_xml():
        return _XmlSerializer.doc_from_xml(
            'StartRoleOperation',
            '<OperationType>StartRoleOperation</OperationType>')

    @staticmethod
    def start_roles_operation_to_xml(role_names):
        xml = _XmlSerializer.data_to_xml(
            [('OperationType', 'StartRolesOperation')])
        xml += '<Roles>'
        for role_name in role_names:
            xml += _XmlSerializer.data_to_xml([('Name', role_name)])
        xml += '</Roles>'
        return _XmlSerializer.doc_from_xml('StartRolesOperation', xml)

    @staticmethod
    def windows_configuration_to_xml(configuration):
        xml = _XmlSerializer.data_to_xml(
            [('ConfigurationSetType', configuration.configuration_set_type),
             ('ComputerName', configuration.computer_name),
             ('AdminPassword', configuration.admin_password),
             ('ResetPasswordOnFirstLogon',
              configuration.reset_password_on_first_logon,
              _lower),
             ('EnableAutomaticUpdates',
              configuration.enable_automatic_updates,
              _lower),
             ('TimeZone', configuration.time_zone)])

        if configuration.domain_join is not None:
            xml += '<DomainJoin>'
            xml += '<Credentials>'
            xml += _XmlSerializer.data_to_xml(
                [('Domain', configuration.domain_join.credentials.domain),
                 ('Username', configuration.domain_join.credentials.username),
                 ('Password', configuration.domain_join.credentials.password)])
            xml += '</Credentials>'
            xml += _XmlSerializer.data_to_xml(
                [('JoinDomain', configuration.domain_join.join_domain),
                 ('MachineObjectOU',
                  configuration.domain_join.machine_object_ou)])
            xml += '</DomainJoin>'
        if configuration.stored_certificate_settings is not None:
            xml += '<StoredCertificateSettings>'
            for cert in configuration.stored_certificate_settings:
                xml += '<CertificateSetting>'
                xml += _XmlSerializer.data_to_xml(
                    [('StoreLocation', cert.store_location),
                     ('StoreName', cert.store_name),
                     ('Thumbprint', cert.thumbprint)])
                xml += '</CertificateSetting>'
            xml += '</StoredCertificateSettings>'
        if configuration.win_rm is not None:
            xml += '<WinRM><Listeners>'
            for listener in configuration.win_rm.listeners:
                xml += '<Listener>'
                xml += _XmlSerializer.data_to_xml(
                    [('Protocol', listener.protocol),
                     ('CertificateThumbprint', listener.certificate_thumbprint)])
                xml += '</Listener>'
            xml += '</Listeners></WinRM>'
        xml += _XmlSerializer.data_to_xml(
            [('AdminUsername', configuration.admin_username),
             ('CustomData', configuration.custom_data, _encode_base64)])
        if configuration.additional_unattend_content and configuration.additional_unattend_content.passes:
            xml += '<AdditionalUnattendContent><Passes>'
            for unattend_pass in configuration.additional_unattend_content.passes:
                xml += _XmlSerializer.data_to_xml(
                    [('PassName', unattend_pass.pass_name)])
                if unattend_pass.components:
                    xml += '<Components>'
                    for comp in unattend_pass.components:
                        xml += '<UnattendComponent>'
                        xml += _XmlSerializer.data_to_xml(
                            [('ComponentName', comp.component_name)])
                        if comp.component_settings:
                            xml += '<ComponentSettings>'
                            for setting in comp.component_settings:
                                xml += '<ComponentSetting>'
                                xml += _XmlSerializer.data_to_xml(
                                    [('SettingName', setting.setting_name),
                                     ('Content', setting.content)])
                                xml += '</ComponentSetting>'
                            xml += '</ComponentSettings>'
                        xml += '</UnattendComponent>'
                    xml += '</Components>'
            xml += '</Passes></AdditionalUnattendContent>'

        return xml

    @staticmethod
    def linux_configuration_to_xml(configuration):
        xml = _XmlSerializer.data_to_xml(
            [('ConfigurationSetType', configuration.configuration_set_type),
             ('HostName', configuration.host_name),
             ('UserName', configuration.user_name),
             ('UserPassword', configuration.user_password),
             ('DisableSshPasswordAuthentication',
              configuration.disable_ssh_password_authentication,
              _lower)])

        if configuration.ssh is not None:
            xml += '<SSH>'
            xml += '<PublicKeys>'
            for key in configuration.ssh.public_keys:
                xml += '<PublicKey>'
                xml += _XmlSerializer.data_to_xml(
                    [('Fingerprint', key.fingerprint),
                     ('Path', key.path)])
                xml += '</PublicKey>'
            xml += '</PublicKeys>'
            xml += '<KeyPairs>'
            for key in configuration.ssh.key_pairs:
                xml += '<KeyPair>'
                xml += _XmlSerializer.data_to_xml(
                    [('Fingerprint', key.fingerprint),
                     ('Path', key.path)])
                xml += '</KeyPair>'
            xml += '</KeyPairs>'
            xml += '</SSH>'

        xml += _XmlSerializer.data_to_xml(
            [('CustomData', configuration.custom_data, _encode_base64)])

        return xml

    @staticmethod
    def network_configuration_to_xml(configuration):
        xml = _XmlSerializer.data_to_xml(
            [('ConfigurationSetType', configuration.configuration_set_type)])
        xml += '<InputEndpoints>'
        for endpoint in configuration.input_endpoints:
            xml += '<InputEndpoint>'
            xml += _XmlSerializer.data_to_xml(
                [('LoadBalancedEndpointSetName',
                  endpoint.load_balanced_endpoint_set_name),
                 ('LocalPort', endpoint.local_port),
                 ('Name', endpoint.name),
                 ('Port', endpoint.port)])

            if endpoint.load_balancer_probe:
                if endpoint.load_balancer_probe.path or\
                    endpoint.load_balancer_probe.port or\
                    endpoint.load_balancer_probe.protocol:
                        xml += '<LoadBalancerProbe>'
                        xml += _XmlSerializer.data_to_xml(
                            [('Path', endpoint.load_balancer_probe.path),
                            ('Port', endpoint.load_balancer_probe.port),
                            ('Protocol', endpoint.load_balancer_probe.protocol)])
                        xml += '</LoadBalancerProbe>'

            xml += _XmlSerializer.data_to_xml(
                [('Protocol', endpoint.protocol),
                 ('EnableDirectServerReturn',
                  endpoint.enable_direct_server_return,
                  _lower),
                 ('IdleTimeoutInMinutes', endpoint.idle_timeout_in_minutes)])

            xml += '</InputEndpoint>'
        xml += '</InputEndpoints>'
        xml += '<SubnetNames>'
        if configuration.subnet_names:
            for name in configuration.subnet_names:
                xml += _XmlSerializer.data_to_xml([('SubnetName', name)])
        xml += '</SubnetNames>'

        if configuration.static_virtual_network_ip_address:
            xml += _XmlSerializer.data_to_xml(
                [('StaticVirtualNetworkIPAddress',
                  configuration.static_virtual_network_ip_address)])

        if configuration.public_ips:
            xml += '<PublicIPs>'
            for public_ip in configuration.public_ips:
                xml += '<PublicIP>'
                xml += _XmlSerializer.data_to_xml(
                    [('Name', public_ip.name),
                     ('IdleTimeoutInMinutes', public_ip.idle_timeout_in_minutes)])
                xml += '</PublicIP>'
            xml += '</PublicIPs>'

        return xml

    @staticmethod
    def role_to_xml(availability_set_name, data_virtual_hard_disks,
                    network_configuration_set, os_virtual_hard_disk, role_name,
                    role_size, role_type, system_configuration_set,
                    resource_extension_references,
                    provision_guest_agent, vm_image_name, media_location):
        xml = _XmlSerializer.data_to_xml([('RoleName', role_name),
                                          ('RoleType', role_type)])

        if system_configuration_set or network_configuration_set:
            xml += '<ConfigurationSets>'

            if system_configuration_set is not None:
                xml += '<ConfigurationSet>'
                if isinstance(system_configuration_set, WindowsConfigurationSet):
                    xml += _XmlSerializer.windows_configuration_to_xml(
                        system_configuration_set)
                elif isinstance(system_configuration_set, LinuxConfigurationSet):
                    xml += _XmlSerializer.linux_configuration_to_xml(
                        system_configuration_set)
                xml += '</ConfigurationSet>'

            if network_configuration_set is not None:
                xml += '<ConfigurationSet>'
                xml += _XmlSerializer.network_configuration_to_xml(
                    network_configuration_set)
                xml += '</ConfigurationSet>'

            xml += '</ConfigurationSets>'

        if resource_extension_references:
            xml += '<ResourceExtensionReferences>'
            for ext in resource_extension_references:
                xml += '<ResourceExtensionReference>'
                xml += _XmlSerializer.data_to_xml(
                    [('ReferenceName', ext.reference_name),
                     ('Publisher', ext.publisher),
                     ('Name', ext.name),
                     ('Version', ext.version)])
                if ext.resource_extension_parameter_values:
                    xml += '<ResourceExtensionParameterValues>'
                    for val in ext.resource_extension_parameter_values:
                        xml += '<ResourceExtensionParameterValue>'
                        xml += _XmlSerializer.data_to_xml(
                            [('Key', val.key),
                             ('Value', val.value),
                             ('Type', val.type)])
                        xml += '</ResourceExtensionParameterValue>'
                    xml += '</ResourceExtensionParameterValues>'
                xml += '</ResourceExtensionReference>'
            xml += '</ResourceExtensionReferences>'

        xml += _XmlSerializer.data_to_xml(
            [('VMImageName', vm_image_name),
             ('MediaLocation', media_location),
             ('AvailabilitySetName', availability_set_name)])

        if data_virtual_hard_disks is not None:
            xml += '<DataVirtualHardDisks>'
            for hd in data_virtual_hard_disks:
                xml += '<DataVirtualHardDisk>'
                xml += _XmlSerializer.data_to_xml(
                    [('HostCaching', hd.host_caching),
                     ('DiskLabel', hd.disk_label),
                     ('DiskName', hd.disk_name),
                     ('Lun', hd.lun),
                     ('LogicalDiskSizeInGB', hd.logical_disk_size_in_gb),
                     ('MediaLink', hd.media_link),
                     ('SourceMediaLink', hd.source_media_link)])
                xml += '</DataVirtualHardDisk>'
            xml += '</DataVirtualHardDisks>'

        if os_virtual_hard_disk is not None:
            xml += '<OSVirtualHardDisk>'
            xml += _XmlSerializer.data_to_xml(
                [('HostCaching', os_virtual_hard_disk.host_caching),
                 ('DiskLabel', os_virtual_hard_disk.disk_label),
                 ('DiskName', os_virtual_hard_disk.disk_name),
                 ('MediaLink', os_virtual_hard_disk.media_link),
                 ('SourceImageName', os_virtual_hard_disk.source_image_name),
                 ('OS', os_virtual_hard_disk.os),
                 ('RemoteSourceImageLink', os_virtual_hard_disk.remote_source_image_link)])
            xml += '</OSVirtualHardDisk>'

        xml += _XmlSerializer.data_to_xml(
            [('RoleSize', role_size),
             ('ProvisionGuestAgent', provision_guest_agent, _lower)])

        return xml

    @staticmethod
    def add_role_to_xml(role_name, system_configuration_set,
                        os_virtual_hard_disk, role_type,
                        network_configuration_set, availability_set_name,
                        data_virtual_hard_disks, role_size,
                        resource_extension_references, provision_guest_agent,
                        vm_image_name, media_location):
        xml = _XmlSerializer.role_to_xml(
            availability_set_name,
            data_virtual_hard_disks,
            network_configuration_set,
            os_virtual_hard_disk,
            role_name,
            role_size,
            role_type,
            system_configuration_set,
            resource_extension_references,
            provision_guest_agent,
            vm_image_name,
            media_location)
        return _XmlSerializer.doc_from_xml('PersistentVMRole', xml)

    @staticmethod
    def update_role_to_xml(role_name, os_virtual_hard_disk, role_type,
                           network_configuration_set, availability_set_name,
                           data_virtual_hard_disks, role_size,
                           resource_extension_references,
                           provision_guest_agent):
        xml = _XmlSerializer.role_to_xml(
            availability_set_name,
            data_virtual_hard_disks,
            network_configuration_set,
            os_virtual_hard_disk,
            role_name,
            role_size,
            role_type,
            None,
            resource_extension_references,
            provision_guest_agent,
            None,
            None)
        return _XmlSerializer.doc_from_xml('PersistentVMRole', xml)

    @staticmethod
    def capture_role_to_xml(post_capture_action, target_image_name,
                            target_image_label, provisioning_configuration):
        xml = _XmlSerializer.data_to_xml(
            [('OperationType', 'CaptureRoleOperation'),
             ('PostCaptureAction', post_capture_action)])

        if provisioning_configuration is not None:
            xml += '<ProvisioningConfiguration>'
            if isinstance(provisioning_configuration, WindowsConfigurationSet):
                xml += _XmlSerializer.windows_configuration_to_xml(
                    provisioning_configuration)
            elif isinstance(provisioning_configuration, LinuxConfigurationSet):
                xml += _XmlSerializer.linux_configuration_to_xml(
                    provisioning_configuration)
            xml += '</ProvisioningConfiguration>'

        xml += _XmlSerializer.data_to_xml(
            [('TargetImageLabel', target_image_label),
             ('TargetImageName', target_image_name)])

        return _XmlSerializer.doc_from_xml('CaptureRoleOperation', xml)

    @staticmethod
    def replicate_image_to_xml(regions, offer, sku, version):
        xml = '<TargetLocations>'
        for region in regions:
            xml += _XmlSerializer.data_to_xml([('Region', region)])
        xml += '</TargetLocations>'
        xml += '<ComputeImageAttributes>'
        xml += _XmlSerializer.data_to_xml(
            [
                ('Offer', offer),
                ('Sku', sku),
                ('Version', version)
            ]
        )
        xml += '</ComputeImageAttributes>'

        return _XmlSerializer.doc_from_xml('ReplicationInput', xml)

    @staticmethod
    def virtual_machine_deployment_to_xml(deployment_name, deployment_slot,
                                          label, role_name,
                                          system_configuration_set,
                                          os_virtual_hard_disk, role_type,
                                          network_configuration_set,
                                          availability_set_name,
                                          data_virtual_hard_disks, role_size,
                                          virtual_network_name,
                                          resource_extension_references,
                                          provision_guest_agent,
                                          vm_image_name,
                                          media_location,
                                          dns_servers,
                                          reserved_ip_name):
        xml = _XmlSerializer.data_to_xml([('Name', deployment_name),
                                          ('DeploymentSlot', deployment_slot),
                                          ('Label', label)])
        xml += '<RoleList>'
        xml += '<Role>'
        xml += _XmlSerializer.role_to_xml(
            availability_set_name,
            data_virtual_hard_disks,
            network_configuration_set,
            os_virtual_hard_disk,
            role_name,
            role_size,
            role_type,
            system_configuration_set,
            resource_extension_references,
            provision_guest_agent,
            vm_image_name,
            media_location)
        xml += '</Role>'
        xml += '</RoleList>'

        xml += _XmlSerializer.data_to_xml(
            [('VirtualNetworkName', virtual_network_name)])

        if dns_servers:
            xml += '<Dns><DnsServers>'
            for dns_server in dns_servers:
                xml += '<DnsServer>'
                xml += _XmlSerializer.data_to_xml(
                    [('Name', dns_server.name),
                     ('Address', dns_server.address)])
                xml += '</DnsServer>'
            xml += '</DnsServers></Dns>'

        xml += _XmlSerializer.data_to_xml(
            [('ReservedIPName', reserved_ip_name)])

        return _XmlSerializer.doc_from_xml('Deployment', xml)

    @staticmethod
    def capture_vm_image_to_xml(options):
        return _XmlSerializer.doc_from_data(
            'CaptureRoleAsVMImageOperation ',
            [('OperationType', 'CaptureRoleAsVMImageOperation'),
             ('OSState', options.os_state),
             ('VMImageName', options.vm_image_name),
             ('VMImageLabel', options.vm_image_label),
             ('Description', options.description),
             ('Language', options.language),
             ('ImageFamily', options.image_family),
             ('RecommendedVMSize', options.recommended_vm_size)])

    @staticmethod
    def create_vm_image_to_xml(image):
        xml = _XmlSerializer.data_to_xml(
            [('Name', image.name),
            ('Label', image.label),
            ('Description', image.description)])

        os_disk = image.os_disk_configuration
        xml += '<OSDiskConfiguration>'
        xml += _XmlSerializer.data_to_xml(
            [('HostCaching', os_disk.host_caching),
            ('OSState', os_disk.os_state),
            ('OS', os_disk.os),
            ('MediaLink', os_disk.media_link)])
        xml += '</OSDiskConfiguration>'

        if image.data_disk_configurations:
            xml += '<DataDiskConfigurations>'
            for data_disk in image.data_disk_configurations:
                xml += '<DataDiskConfiguration>'
                xml += _XmlSerializer.data_to_xml(
                    [('HostCaching', data_disk.host_caching),
                    ('Lun', data_disk.lun),
                    ('MediaLink', data_disk.media_link),
                    ('LogicalDiskSizeInGB', data_disk.logical_disk_size_in_gb)])
                xml += '</DataDiskConfiguration>'
            xml += '</DataDiskConfigurations>'

        xml += _XmlSerializer.data_to_xml(
            [('Language', image.language),
            ('ImageFamily', image.image_family),
            ('RecommendedVMSize', image.recommended_vm_size),
            ('Eula', image.eula),
            ('IconUri', image.icon_uri),
            ('SmallIconUri', image.small_icon_uri),
            ('PrivacyUri', image.privacy_uri),
            ('PublishedDate', image.published_date),
            ('ShowInGui', image.show_in_gui, _lower)])

        return _XmlSerializer.doc_from_xml('VMImage', xml)

    @staticmethod
    def update_vm_image_to_xml(image):
        xml = _XmlSerializer.data_to_xml(
            [('Label', image.label),
            ('Description', image.description)])

        os_disk = image.os_disk_configuration
        xml += '<OSDiskConfiguration>'
        xml += _XmlSerializer.data_to_xml(
            [('HostCaching', os_disk.host_caching)])
        xml += '</OSDiskConfiguration>'

        xml += '<DataDiskConfigurations>'
        for data_disk in image.data_disk_configurations:
            xml += '<DataDiskConfiguration>'
            xml += _XmlSerializer.data_to_xml(
                [('Name', data_disk.name),
                ('HostCaching', data_disk.host_caching),
                ('Lun', data_disk.lun)])
            xml += '</DataDiskConfiguration>'
        xml += '</DataDiskConfigurations>'

        xml += _XmlSerializer.data_to_xml(
            [('Language', image.language),
            ('ImageFamily', image.image_family),
            ('RecommendedVMSize', image.recommended_vm_size),
            ('Eula', image.eula),
            ('IconUri', image.icon_uri),
            ('SmallIconUri', image.small_icon_uri),
            ('PrivacyUri', image.privacy_uri),
            ('PublishedDate', image.published_date),
            ('ShowInGui', image.show_in_gui, _lower)])

        return _XmlSerializer.doc_from_xml('VMImage', xml)

    @staticmethod
    def update_os_image_to_xml(image):
        # Explicitly replace empty string by None to avoid serialization 
        # of this field, since the API answers "BadRequest" for empty string.
        if not image.published_date:
            image.published_date = None
        xml = _XmlSerializer.data_to_xml(
            [
                ('Label', image.label),
                ('Eula', image.eula),
                ('Description', image.description),
                ('ImageFamily', image.image_family),
                ('ShowInGui', image.show_in_gui, _lower),
                ('PublishedDate', image.published_date),
                ('IconUri', image.icon_uri),
                ('PrivacyUri', image.privacy_uri),
                ('RecommendedVMSize', image.recommended_vm_size),
                ('SmallIconUri', image.small_icon_uri),
                ('Language', image.language)
            ]
        )
        return _XmlSerializer.doc_from_xml('OSImage', xml)

    @staticmethod
    def create_website_to_xml(webspace_name, website_name, geo_region, plan,
                              host_names, compute_mode, server_farm, site_mode):
        xml = '<HostNames xmlns:a="http://schemas.microsoft.com/2003/10/Serialization/Arrays">'
        for host_name in host_names:
            xml += '<a:string>{0}</a:string>'.format(host_name)
        xml += '</HostNames>'
        xml += _XmlSerializer.data_to_xml(
            [('Name', website_name),
             ('ComputeMode', compute_mode),
             ('ServerFarm', server_farm),
             ('SiteMode', site_mode)])
        xml += '<WebSpaceToCreate>'
        xml += _XmlSerializer.data_to_xml(
            [('GeoRegion', geo_region),
             ('Name', webspace_name),
             ('Plan', plan)])
        xml += '</WebSpaceToCreate>'
        return _XmlSerializer.doc_from_xml('Site', xml)

    @staticmethod
    def update_website_to_xml(state):
        xml = _XmlSerializer.data_to_xml(
            [('State', state)])
        return _XmlSerializer.doc_from_xml('Site', xml)

    @staticmethod
    def create_reserved_ip_to_xml(name, label, location):
        return _XmlSerializer.doc_from_data(
            'ReservedIP',
            [('Name', name),
             ('Label', label),
             ('Location', location)])

    @staticmethod
    def associate_reserved_ip_to_xml(
        service_name, deployment_name, virtual_ip_name
    ):
        xml = _XmlSerializer.data_to_xml([
            ('ServiceName', service_name),
            ('DeploymentName', deployment_name),
        ])
        if virtual_ip_name:
            xml += _XmlSerializer.data_to_xml(
                [('VirtualIPName', virtual_ip_name)]
            )
        return _XmlSerializer.doc_from_xml('ReservedIPAssociation', xml)

    @staticmethod
    def dns_server_to_xml(name, address):
        return _XmlSerializer.doc_from_data(
            'DnsServer',
            [('Name', name),
             ('Address', address)])

    @staticmethod
    def role_instances_to_xml(role_instances):
        xml = ''
        for name in role_instances:
            xml += _XmlSerializer.data_to_xml([('Name', name)])
        return _XmlSerializer.doc_from_xml('RoleInstances ', xml)

    @staticmethod
    def data_to_xml(data):
        return _data_to_xml(data)

    @staticmethod
    def doc_from_xml(document_element_name, inner_xml):
        '''Wraps the specified xml in an xml root element with default azure
        namespaces'''
        xml = ''.join(['<', document_element_name,
                      ' xmlns:i="http://www.w3.org/2001/XMLSchema-instance"',
                      ' xmlns="http://schemas.microsoft.com/windowsazure">'])
        xml += inner_xml
        xml += ''.join(['</', document_element_name, '>'])
        return xml

    @staticmethod
    def doc_from_data(document_element_name, data, extended_properties=None):
        xml = _XmlSerializer.data_to_xml(data)
        if extended_properties is not None:
            xml += _XmlSerializer.extended_properties_dict_to_xml_fragment(
                extended_properties)
        return _XmlSerializer.doc_from_xml(document_element_name, xml)

    @staticmethod
    def extended_properties_dict_to_xml_fragment(extended_properties):
        xml = ''
        if extended_properties is not None and len(extended_properties) > 0:
            xml += '<ExtendedProperties>'
            for key, val in extended_properties.items():
                xml += ''.join(['<ExtendedProperty>',
                                '<Name>',
                                _str(key),
                                '</Name>',
                               '<Value>',
                               _str(val),
                               '</Value>',
                               '</ExtendedProperty>'])
            xml += '</ExtendedProperties>'
        return xml


class _SqlManagementXmlSerializer(object):

    @staticmethod
    def create_server_to_xml(admin_login, admin_password, location):
        return _SqlManagementXmlSerializer.doc_from_data(
            'Server',
            [('AdministratorLogin', admin_login),
             ('AdministratorLoginPassword', admin_password),
             ('Location', location)],
             'http://schemas.microsoft.com/sqlazure/2010/12/')

    @staticmethod
    def set_server_admin_password_to_xml(admin_password):
        return _SqlManagementXmlSerializer.doc_from_xml(
            'AdministratorLoginPassword', admin_password,
            'http://schemas.microsoft.com/sqlazure/2010/12/')

    @staticmethod
    def create_firewall_rule_to_xml(name, start_ip_address, end_ip_address):
        return _SqlManagementXmlSerializer.doc_from_data(
            'ServiceResource',
            [('Name', name),
             ('StartIPAddress', start_ip_address),
             ('EndIPAddress', end_ip_address)])

    @staticmethod
    def update_firewall_rule_to_xml(name, start_ip_address, end_ip_address):
        return _SqlManagementXmlSerializer.doc_from_data(
            'ServiceResource',
            [('Name', name),
             ('StartIPAddress', start_ip_address),
             ('EndIPAddress', end_ip_address)])

    @staticmethod
    def create_database_to_xml(name, service_objective_id, edition, collation_name,
                max_size_bytes):
        return _SqlManagementXmlSerializer.doc_from_data(
            'ServiceResource',
            [('Name', name),
             ('Edition', edition),
             ('CollationName', collation_name),
             ('MaxSizeBytes', max_size_bytes),
             ('ServiceObjectiveId', service_objective_id)])

    @staticmethod
    def update_database_to_xml(name, service_objective_id, edition,
                               max_size_bytes):
        return _SqlManagementXmlSerializer.doc_from_data(
            'ServiceResource',
            [('Name', name),
             ('Edition', edition),
             ('MaxSizeBytes', max_size_bytes),
             ('ServiceObjectiveId', service_objective_id)])

    @staticmethod
    def xml_to_create_server_response(xmlstr):
        xmldoc = minidom.parseString(xmlstr)
        element = xmldoc.documentElement

        response = CreateServerResponse()
        response.server_name = element.firstChild.nodeValue
        response.fully_qualified_domain_name = element.getAttribute('FullyQualifiedDomainName')

        return response

    @staticmethod
    def data_to_xml(data):
        return _data_to_xml(data)

    @staticmethod
    def doc_from_xml(document_element_name, inner_xml,
                     xmlns='http://schemas.microsoft.com/windowsazure'):
        '''Wraps the specified xml in an xml root element with default azure
        namespaces'''
        xml = ''.join(['<', document_element_name,
                      ' xmlns="{0}">'.format(xmlns)])
        xml += inner_xml
        xml += ''.join(['</', document_element_name, '>'])
        return xml

    @staticmethod
    def doc_from_data(document_element_name, data,
                      xmlns='http://schemas.microsoft.com/windowsazure'):
        xml = _SqlManagementXmlSerializer.data_to_xml(data)
        return _SqlManagementXmlSerializer.doc_from_xml(
            document_element_name, xml, xmlns)


def _parse_bool(value):
    if value.lower() == 'true':
        return True
    return False


class _ServiceBusManagementXmlSerializer(object):

    @staticmethod
    def namespace_to_xml(region):
        '''Converts a service bus namespace description to xml

        The xml format:
<?xml version="1.0" encoding="utf-8" standalone="yes"?>
<entry xmlns="http://www.w3.org/2005/Atom">
    <content type="application/xml">
        <NamespaceDescription
            xmlns="http://schemas.microsoft.com/netservices/2010/10/servicebus/connect">
            <Region>West US</Region>
        </NamespaceDescription>
    </content>
</entry>
        '''
        body = '<NamespaceDescription xmlns="http://schemas.microsoft.com/netservices/2010/10/servicebus/connect">'
        body += ''.join(['<Region>', region, '</Region>'])
        body += '</NamespaceDescription>'

        return _create_entry(body)

    @staticmethod
    def xml_to_namespace(xmlstr):
        '''Converts xml response to service bus namespace

        The xml format for namespace:
<entry>
<id>uuid:00000000-0000-0000-0000-000000000000;id=0000000</id>
<title type="text">myunittests</title>
<updated>2012-08-22T16:48:10Z</updated>
<content type="application/xml">
    <NamespaceDescription
        xmlns="http://schemas.microsoft.com/netservices/2010/10/servicebus/connect"
        xmlns:i="http://www.w3.org/2001/XMLSchema-instance">
    <Name>myunittests</Name>
    <Region>West US</Region>
    <DefaultKey>0000000000000000000000000000000000000000000=</DefaultKey>
    <Status>Active</Status>
    <CreatedAt>2012-08-22T16:48:10.217Z</CreatedAt>
    <AcsManagementEndpoint>https://myunittests-sb.accesscontrol.windows.net/</AcsManagementEndpoint>
    <ServiceBusEndpoint>https://myunittests.servicebus.windows.net/</ServiceBusEndpoint>
    <ConnectionString>Endpoint=sb://myunittests.servicebus.windows.net/;SharedSecretIssuer=owner;SharedSecretValue=0000000000000000000000000000000000000000000=</ConnectionString>
    <SubscriptionId>00000000000000000000000000000000</SubscriptionId>
    <Enabled>true</Enabled>
    </NamespaceDescription>
</content>
</entry>
        '''
        xmldoc = minidom.parseString(xmlstr)
        namespace = ServiceBusNamespace()

        mappings = (
            ('Name', 'name', None),
            ('Region', 'region', None),
            ('DefaultKey', 'default_key', None),
            ('Status', 'status', None),
            ('CreatedAt', 'created_at', None),
            ('AcsManagementEndpoint', 'acs_management_endpoint', None),
            ('ServiceBusEndpoint', 'servicebus_endpoint', None),
            ('ConnectionString', 'connection_string', None),
            ('SubscriptionId', 'subscription_id', None),
            ('Enabled', 'enabled', _parse_bool),
        )

        for desc in _MinidomXmlToObject.get_children_from_path(
            xmldoc,
            'entry',
            'content',
            'NamespaceDescription'):
            for xml_name, field_name, conversion_func in mappings:
                node_value = _MinidomXmlToObject.get_first_child_node_value(desc, xml_name)
                if node_value is not None:
                    if conversion_func is not None:
                        node_value = conversion_func(node_value)
                    setattr(namespace, field_name, node_value)

        return namespace

    @staticmethod
    def xml_to_region(xmlstr):
        '''Converts xml response to service bus region

        The xml format for region:
<entry>
<id>uuid:157c311f-081f-4b4a-a0ba-a8f990ffd2a3;id=1756759</id>
<title type="text"></title>
<updated>2013-04-10T18:25:29Z</updated>
<content type="application/xml">
    <RegionCodeDescription
        xmlns="http://schemas.microsoft.com/netservices/2010/10/servicebus/connect"
        xmlns:i="http://www.w3.org/2001/XMLSchema-instance">
    <Code>East Asia</Code>
    <FullName>East Asia</FullName>
    </RegionCodeDescription>
</content>
</entry>
          '''
        xmldoc = minidom.parseString(xmlstr)
        region = ServiceBusRegion()

        for desc in _MinidomXmlToObject.get_children_from_path(xmldoc, 'entry', 'content',
                                            'RegionCodeDescription'):
            node_value = _MinidomXmlToObject.get_first_child_node_value(desc, 'Code')
            if node_value is not None:
                region.code = node_value
            node_value = _MinidomXmlToObject.get_first_child_node_value(desc, 'FullName')
            if node_value is not None:
                region.fullname = node_value

        return region

    @staticmethod
    def xml_to_namespace_availability(xmlstr):
        '''Converts xml response to service bus namespace availability

        The xml format:
<?xml version="1.0" encoding="utf-8"?>
<entry xmlns="http://www.w3.org/2005/Atom">
    <id>uuid:9fc7c652-1856-47ab-8d74-cd31502ea8e6;id=3683292</id>
    <title type="text"></title>
    <updated>2013-04-16T03:03:37Z</updated>
    <content type="application/xml">
        <NamespaceAvailability
            xmlns="http://schemas.microsoft.com/netservices/2010/10/servicebus/connect"
            xmlns:i="http://www.w3.org/2001/XMLSchema-instance">
            <Result>false</Result>
        </NamespaceAvailability>
    </content>
</entry>
        '''
        xmldoc = minidom.parseString(xmlstr)
        availability = AvailabilityResponse()

        for desc in _MinidomXmlToObject.get_children_from_path(xmldoc, 'entry', 'content',
                                            'NamespaceAvailability'):
            node_value = _MinidomXmlToObject.get_first_child_node_value(desc, 'Result')
            if node_value is not None:
                availability.result = _parse_bool(node_value)

        return availability

    @staticmethod
    def odata_converter(data, str_type):
        ''' Convert odata type
        http://www.odata.org/documentation/odata-version-2-0/overview#AbstractTypeSystem
        To be completed
        '''
        if not str_type:
            return _str(data)
        if str_type in ["Edm.Single", "Edm.Double"]:
            return float(data)
        elif "Edm.Int" in str_type:
            return int(data)
        else:
            return _str(data)

    @staticmethod
    def xml_to_metrics(xmlstr, object_type):
        '''Converts xml response to service bus metrics objects

        The xml format for MetricProperties
<entry>
    <id>https://sbgm.windows.net/Metrics(\'listeners.active\')</id>
    <title/>
    <updated>2014-10-09T11:56:50Z</updated>
    <author>
        <name/>
    </author>
    <content type="application/xml">
        <m:properties>
            <d:Name>listeners.active</d:Name>
            <d:PrimaryAggregation>Average</d:PrimaryAggregation>
            <d:Unit>Count</d:Unit>
            <d:DisplayName>Active listeners</d:DisplayName>
        </m:properties>
    </content>
</entry>

        The xml format for MetricValues
    <entry>
        <id>https://sbgm.windows.net/MetricValues(datetime\'2014-10-02T00:00:00Z\')</id>
        <title/>
        <updated>2014-10-09T18:38:28Z</updated>
        <author>
            <name/>
        </author>
        <content type="application/xml">
            <m:properties>
                <d:Timestamp m:type="Edm.DateTime">2014-10-02T00:00:00Z</d:Timestamp>
                <d:Min m:type="Edm.Int64">-118</d:Min>
                <d:Max m:type="Edm.Int64">15</d:Max>
                <d:Average m:type="Edm.Single">-78.44444</d:Average>
                <d:Total m:type="Edm.Int64">0</d:Total>
            </m:properties>
        </content>
    </entry>
        '''

        xmldoc = minidom.parseString(xmlstr)
        return_obj = object_type()

        members = dict(vars(return_obj))

        # Only one entry here
        for xml_entry in _MinidomXmlToObject.get_children_from_path(xmldoc,
                                                 'entry'):
            for node in _MinidomXmlToObject.get_children_from_path(xml_entry,
                                                'content',
                                                'properties'):
                for name in members:
                    xml_name = _get_serialization_name(name)
                    children = _MinidomXmlToObject.get_child_nodes(node, xml_name)
                    if not children:
                        continue
                    child = children[0]
                    node_type = child.getAttributeNS("http://schemas.microsoft.com/ado/2007/08/dataservices/metadata", 'type')
                    node_value = _ServiceBusManagementXmlSerializer.odata_converter(child.firstChild.nodeValue, node_type)
                    setattr(return_obj, name, node_value)
            for name, value in _MinidomXmlToObject.get_entry_properties_from_node(
                xml_entry,
                include_id=True,
                use_title_as_id=False).items():
                if name in members:
                    continue  # Do not override if already members
                setattr(return_obj, name, value)
        return return_obj


class _SchedulerManagementXmlSerializer(object):

    @staticmethod
    def create_cloud_service_to_xml(label, description, geo_region):
        '''
        <CloudService xmlns:i="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://schemas.microsoft.com/windowsazure">
          <Label>MyApp3</Label>
          <Description>My Cloud Service for app3</Description>
          <GeoRegion>South Central US</GeoRegion>
        </CloudService>
        '''
        body = '<CloudService xmlns:i="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://schemas.microsoft.com/windowsazure">'
        body += ''.join(['<Label>', label, '</Label>'])
        body += ''.join(['<Description>', description, '</Description>'])
        body += ''.join(['<GeoRegion>', geo_region, '</GeoRegion>'])
        body += '</CloudService>'

        return body

    @staticmethod
    def create_job_collection_to_xml(plan):
        '''
        <Resource xmlns:i="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://schemas.microsoft.com/windowsazure">
        <IntrinsicSettings>
            <Plan>Standard</Plan>
            <Quota>
                <MaxJobCount>10</MaxJobCount>
                <MaxRecurrence>
                    <Frequency>Second</Frequency>
                    <Interval>1</Interval>
                </MaxRecurrence>
            </Quota>
        </IntrinsicSettings>
        </Resource>
        '''

        if plan not in ["Free", "Standard"]:
            raise ValueError("Plan: Invalid option must be 'Standard' or 'Free'")

        body = '<Resource xmlns:i="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://schemas.microsoft.com/windowsazure"><IntrinsicSettings>'
        body += ''.join(['<plan>', plan, '</plan>'])
        body += '</IntrinsicSettings></Resource>'

        return body
