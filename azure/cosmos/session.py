#The MIT License (MIT)
#Copyright (c) 2014 Microsoft Corporation

#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:

#The above copyright notice and this permission notice shall be included in all
#copies or substantial portions of the Software.

#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

"""Session Consistency Tracking in the Azure Cosmos database service.
"""

import sys, traceback
import threading

import azure.cosmos.base as base
import azure.cosmos.http_constants as http_constants
from azure.cosmos.vector_session_token import VectorSessionToken
from azure.cosmos.errors import HTTPFailure

class SessionContainer(object):

    def __init__(self):
        self.collection_name_to_rid = {}
        self.rid_to_session_token = {}
        self.session_lock = threading.RLock()

    def get_session_token(self, resource_path):
        """
        Get Session Token for collection_link
        
        :param str resource_path:
            Self link / path to the resource

        :return:
            Session Token dictionary for the collection_id
        :rtype:
            dict
        """

        with self.session_lock:
            is_name_based = base.IsNameBased(resource_path)
            collection_rid = ''
            session_token = ''

            try:
                if is_name_based:
                    # get the collection name
                    collection_name = base.GetItemContainerLink(resource_path)
                    collection_rid = self.collection_name_to_rid[collection_name]
                else:
                    collection_rid = base.GetItemContainerLink(resource_path)

                if collection_rid in self.rid_to_session_token:
                    token_dict = self.rid_to_session_token[collection_rid]
                    session_token_list = []
                    for key in token_dict.keys():
                        session_token_list.append("{0}:{1}".format(key, token_dict[key].convert_to_string()))
                    session_token = ','.join(session_token_list)
                    return session_token
                else:
                    # return empty token if not found 
                    return ''
            except: 
                return ''

    def set_session_token(self, response_result, response_headers):
        """ 
        Session token must only be updated from response of requests that successfully mutate resource on the 
        server side (write, replace, delete etc) 
        
        :param dict response_result:
        :param dict response_headers:

        :return:
            - None
        """

        ''' there are two pieces of information that we need to update session token- 
        self link which has the rid representation of the resource, and
        x-ms-alt-content-path which is the string representation of the resource'''

        with self.session_lock:
            collection_rid = ''
            collection_name = ''

            try:
                self_link = response_result['_self']

                ''' extract alternate content path from the response_headers 
                (only document level resource updates will have this), 
                and if not present, then we can assume that we don't have to update
                session token for this request'''
                alt_content_path = ''
                alt_content_path_key = http_constants.HttpHeaders.AlternateContentPath
                response_result_id_key = u'id'
                response_result_id = None
                if alt_content_path_key in response_headers:
                    alt_content_path = response_headers[http_constants.HttpHeaders.AlternateContentPath]
                    response_result_id = response_result[response_result_id_key]
                else:
                    return
                collection_rid, collection_name = base.GetItemContainerInfo(self_link, alt_content_path, response_result_id)
         
            except ValueError:
                return
            except:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                traceback.print_exception(exc_type, exc_value, exc_traceback,
                                  limit=2, file=sys.stdout)
                return

            if collection_name in self.collection_name_to_rid:
                ''' check if the rid for the collection name has changed
                this means that potentially, the collection was deleted
                and recreated
                '''
                existing_rid = self.collection_name_to_rid[collection_name]
                if (collection_rid != existing_rid):
                    ''' flush the session tokens for the old rid, and 
                    update the new rid into the collection name to rid map.
                    '''
                    self.rid_to_session_token[existing_rid] = {}
                    self.collection_name_to_rid[collection_name] = collection_rid

            # parse session token
            parsed_tokens = self.parse_session_token(response_headers)

            # update session token in collection rid to session token map
            if collection_rid in self.rid_to_session_token:
                ''' we need to update the session tokens for 'this' collection
                '''
                for id in parsed_tokens:
                    old_session_token = self.rid_to_session_token[collection_rid][id] if id in self.rid_to_session_token[collection_rid] else None
                    if not old_session_token:
                        self.rid_to_session_token[collection_rid][id] = parsed_tokens[id]
                    else:
                        self.rid_to_session_token[collection_rid][id] = parsed_tokens[id].merge(old_session_token)
                    self.collection_name_to_rid[collection_name] = collection_rid
            else:
                self.rid_to_session_token[collection_rid] = parsed_tokens
                self.collection_name_to_rid[collection_name] = collection_rid

    def clear_session_token(self, response_headers):
        with self.session_lock:
            collection_rid = ''
            alt_content_path = ''
            alt_content_path_key = http_constants.HttpHeaders.AlternateContentPath
            if alt_content_path_key in response_headers:
                    alt_content_path = response_headers[http_constants.HttpHeaders.AlternateContentPath]
                    if alt_content_path in self.collection_name_to_rid:
                        collection_rid = self.collection_name_to_rid[alt_content_path]
                        del self.collection_name_to_rid[alt_content_path]
                        del self.rid_to_session_token[collection_rid]

    @staticmethod
    def parse_session_token(response_headers):
        """ Extracts session token from response headers and parses

        :param dict response_headers:

        :return:
            A dictionary of partition id to session lsn
            for given collection 
        :rtype: dict    
        """

        # extract session token from response header
        session_token = ''
        if http_constants.HttpHeaders.SessionToken in response_headers:
                session_token = response_headers[http_constants.HttpHeaders.SessionToken]

        id_to_sessionlsn = {}
        if session_token is not '':
            ''' extract id, lsn from the token. For p-collection,
            the token will be a concatenation of pairs for each collection'''
            token_pairs = session_token.split(',')
            for token_pair in token_pairs:
                tokens = token_pair.split(':')
                if (len(tokens) == 2):
                    id = tokens[0]
                    sessionToken = VectorSessionToken.create(tokens[1])
                    if sessionToken is None:
                        raise HTTPFailure(http_constants.StatusCodes.INTERNAL_SERVER_ERROR, "Could not parse the received session token: %s" % tokens[1])
                    id_to_sessionlsn[id] = sessionToken
        return id_to_sessionlsn

class Session:
    """ 
    State of a Azure Cosmos session. This session object
    can be shared across clients within the same process
    """

    def __init__(self, url_connection):
        self.url_connection = url_connection
        self.session_container = SessionContainer()
        #include creation time, and some other stats

    def clear_session_token(self, response_headers):
        self.session_container.clear_session_token(response_headers)

    def update_session(self, response_result, response_headers):
        self.session_container.set_session_token(response_result, response_headers)

    def get_session_token(self, resource_path):
        return self.session_container.get_session_token(resource_path)