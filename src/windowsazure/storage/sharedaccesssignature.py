import base64
import hmac
import hashlib

SIGNED_START = 'st'
SIGNED_EXPIRY = 'se'
SIGNED_RESOURCE = 'sr'
SIGNED_PERMISSION = 'sp'
SIGNED_IDENTIFIER = 'si'
SIGNED_SIGNATURE = 'sig'
RESOURCE_BLOB = 'blob'
RESOURCE_CONTAINER = 'container'
SIGNED_RESOURCE_TYPE = 'resource'
SHARED_ACCESS_PERMISSION = 'permission'

class WebResource:
    def __init__(self, path=None, request_url=None, properties={}):
        self.path = path
        self.properties = properties
        self.request_url = request_url

class Permission:
    def __init__(self, path=None, query_string=None):
        self.path = path
        self.query_string = query_string

class SharedAccessPolicy:
    def __init__(self, access_policy, signed_identifier=None):
        self.id = signed_identifier
        self.access_policy = access_policy

class SharedAccessSignature:
    def __init__(self, account_name, account_key, permission_set=None):
        self.account_name = account_name
        self.account_key = account_key
        self.permission_set = permission_set

    def generate_signed_query_string(self, path, resource_type, shared_access_policy):
        query_string = {}
        if shared_access_policy.access_policy.start:
            query_string[SIGNED_START] = shared_access_policy.access_policy.start
        
        query_string[SIGNED_EXPIRY] = shared_access_policy.access_policy.expiry
        query_string[SIGNED_RESOURCE] = resource_type
        query_string[SIGNED_PERMISSION] = shared_access_policy.access_policy.permission

        if shared_access_policy.id:
            query_string[SIGNED_IDENTIFIER] = shared_access_policy.id

        query_string[SIGNED_SIGNATURE] = self._generate_signature(path, resource_type, shared_access_policy)
        return query_string

    def sign_request(self, web_resource):
        if self.permission_set:
            for shared_access_signature in self.permission_set:
                if self._permission_matches_request(shared_access_signature, web_resource, 
                                                    web_resource.properties[SIGNED_RESOURCE_TYPE], 
                                                    web_resource.properties[SHARED_ACCESS_PERMISSION]):
                    if web_resource.request_url.find('?') == -1:
                        web_resource.request_url += '?'
                    else:
                        web_resource.request_url += '&'

                    web_resource.request_url += self._convert_query_string(shared_access_signature.query_string)
                    break
        return web_resource

    def _convert_query_string(self, query_string):
        convert_str = ''
        if query_string.has_key(SIGNED_START):
            convert_str += SIGNED_START + '=' + query_string[SIGNED_START] + '&'
        convert_str += SIGNED_EXPIRY + '=' + query_string[SIGNED_EXPIRY] + '&'
        convert_str += SIGNED_PERMISSION + '=' + query_string[SIGNED_PERMISSION] + '&'
        convert_str += SIGNED_RESOURCE_TYPE + '=' + query_string[SIGNED_RESOURCE] + '&'

        if query_string.has_key(SIGNED_IDENTIFIER):
            convert_str += SIGNED_IDENTIFIER + '=' + query_string[SIGNED_IDENTIFIER] + '&'
        convert_str += SIGNED_SIGNATURE + '=' + query_string[SIGNED_SIGNATURE] + '&'
        return convert_str

    def _generate_signature(self, path, resource_type, shared_access_policy):

        def get_value_to_append(value, no_new_line=False):
            return_value = ''
            if value:
                return_value = value
            if not no_new_line:
                return_value += '\n'
            return return_value

        if path[0] != '/':
            path = '/' + path

        canonicalized_resource = '/' + self.account_name + path;
        string_to_sign = (get_value_to_append(shared_access_policy.access_policy.permission) + 
                          get_value_to_append(shared_access_policy.access_policy.start) +
                          get_value_to_append(shared_access_policy.access_policy.expiry) + 
                          get_value_to_append(canonicalized_resource) +
                          get_value_to_append(shared_access_policy.id, True))

        return self._sign(string_to_sign)

    def _permission_matches_request(self, shared_access_signature, web_resource, resource_type, required_permission):
        required_resource_type = resource_type
        if required_resource_type == RESOURCE_BLOB:
            required_resource_type += RESOURCE_CONTAINER

        for name, value in shared_access_signature.query_string.iteritems():
            if name == SIGNED_RESOURCE and required_resource_type.find(value) == -1:
                return False
            elif name == SIGNED_PERMISSION and required_permission.find(value) == -1:
                return False

        return web_resource.path.find(shared_access_signature.path) != -1

    def _sign(self, string_to_sign):
        decode_account_key = base64.b64decode(self.account_key)
        signed_hmac_sha256 = hmac.HMAC(decode_account_key, string_to_sign, hashlib.sha256)
        return base64.b64encode(signed_hmac_sha256.digest())
        







