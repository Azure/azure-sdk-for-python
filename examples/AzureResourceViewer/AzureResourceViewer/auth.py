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
import adal
import base64
import dateutil
import datetime
import os
from functools import wraps

from flask import url_for, session, abort, redirect, request

from . import app_creds_real as app_creds

authorityUrl = app_creds.AUTHORITY_HOST_URL + '/' + app_creds.TENANT
resource = '00000002-0000-0000-c000-000000000000' #resource of Microsoft.Azure.ActiveDirectory
resource = 'https://management.azure.com/'
resource = 'https://management.core.windows.net/'

templateAuthzUrl = 'https://login.windows.net/' + app_creds.TENANT + '/oauth2/authorize?response_type=code&client_id=<client_id>&redirect_uri=<redirect_uri>&state=<state>&resource=<resource>'


def create_authorization_url(state):
  authorizationUrl = templateAuthzUrl.replace('<client_id>', app_creds.CLIENT_ID)
  authorizationUrl = authorizationUrl.replace('<redirect_uri>', url_for('authorized_view', _external=True))
  authorizationUrl = authorizationUrl.replace('<state>', state)
  authorizationUrl = authorizationUrl.replace('<resource>', resource)
  return authorizationUrl

def unique_auth_state():
    data = os.urandom(48)
    token = base64.b64encode(data, b'-_').decode()
    return token

def get_tokens(auth_code):
    token_response = adal._acquire_token_with_authorization_code(
        authorityUrl,
        app_creds.CLIENT_ID,
        app_creds.CLIENT_SECRET,
        str(auth_code),
        url_for('authorized_view', _external=True),
        resource,
    )
    return token_response

def clear_session_token():
    session['accessToken'] = None
    session['refreshToken'] = None
    session['expiresOn'] = None

def set_session_token_response(token_response):
    access_token = token_response.get('accessToken')
    refresh_token = token_response.get('refreshToken')
    expires_on = token_response.get('expiresOn')
    session['accessToken'] = access_token
    session['refreshToken'] = refresh_token
    session['expiresOn'] = expires_on

EXPIRY_THRESHOLD = datetime.timedelta(seconds=60)

class TokenState(object):
    NoToken = 0
    ExpiredToken = 1
    ValidToken = 2

def is_logged_in():
    state = _get_token_state()
    return state == TokenState.ValidToken or state == TokenState.ExpiredToken

def _get_token_state():
    token = session.get('accessToken')
    expires_on = session.get('expiresOn')
    if token and expires_on:
        expiry = dateutil.parser.parse(expires_on)
        remain = expiry - datetime.datetime.now()
        if remain < EXPIRY_THRESHOLD:
            return TokenState.ExpiredToken
        else:
            return TokenState.ValidToken
    return TokenState.NoToken

def _refresh_token():
    refresh_token = session.get('refreshToken')
    try:
        clear_session_token()
        resp2 = adal.acquire_token_with_refresh_token(
            authorityUrl,
            refresh_token,
            app_creds.CLIENT_ID,
            app_creds.CLIENT_SECRET,
            resource,
        )
        # TODO:
        # we don't get a refreshToken from the response
        # does it mean we are supposed to keep using the same one?
        if 'refreshToken' not in resp2:
            resp2['refreshToken'] = refresh_token
        set_session_token_response(resp2)
    except:
        pass

def require_login(v):
    @wraps(v)
    def authenticating_view(*args, **kwargs):
        token_state = _get_token_state()

        if token_state == TokenState.ExpiredToken:
            _refresh_token()
            token_state = _get_token_state()

        if token_state == TokenState.ValidToken:
            return v(*args, **kwargs)

        return redirect(url_for('login_view', redirect_uri=request.base_url))

    return authenticating_view
