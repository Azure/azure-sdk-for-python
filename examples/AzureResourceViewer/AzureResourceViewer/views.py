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
"""
Routes and views for the flask application.
"""
import json
from datetime import datetime
from flask import render_template, redirect, url_for, request, jsonify, make_response, abort, session
from . import app
from . import models, auth
from azure.common.exceptions import CloudError

app.secret_key = auth.app_creds.SESSION_SECRET

##############################################################################
# Web views

@app.route('/')
@app.route('/home')
def home_view():
    """Renders the home page."""
    return render_template(
        'index.html',
        title='Home Page',
        year=datetime.now().year,
    )

@app.route('/login')
def login_view():
    """Renders the login page."""
    redirect_uri = request.values.get(
        'redirect_uri',
        url_for('account_view', _external=True),
    )
    return render_template(
        'login.html',
        title='Login',
        year=datetime.now().year,
        message='Your login page.',
        redirect_uri=redirect_uri,
    )

@app.route('/logout', methods=['POST'])
def logout_post():
    auth.clear_session_token()
    return redirect(url_for('home_view'))

@app.route('/azurelogin')
def azurelogin_view():
    """Redirects to Azure login page."""
    redirect_uri = request.values.get('redirect_uri')
    session_auth_state = auth.unique_auth_state()
    session['authstate'] = session_auth_state
    session['redirecturiafterauthorized'] = redirect_uri
    auth_url = auth.create_authorization_url(session_auth_state)
    return redirect(auth_url)

@app.route('/authorized')
def authorized_view():
    """Renders the post Azure authorization page."""
    session_auth_state = session.get('authstate')
    auth_code = request.args.get('code')
    auth_state = request.args.get('state')
    if session_auth_state != auth_state:
        abort(401)

    redirect_uri = session.get('redirecturiafterauthorized')

    auth.clear_session_token()
    token_response = auth.get_tokens(auth_code)
    auth.set_session_token_response(token_response)

    if not redirect_uri:
        redirect_uri = url_for('home_view')

    return redirect(redirect_uri)

@app.route('/contact')
def contact_view():
    """Renders the contact page."""
    return render_template(
        'contact.html',
        title='Contact',
        year=datetime.now().year,
        message='Your contact page.'
    )

@app.route('/account')
@auth.require_login
def account_view():
    """Renders the account details."""
    creds = _get_credentials()
    model = models.get_account_details(creds)
    return render_template(
        'account.html',
        title='Account',
        year=datetime.now().year,
        model=model,
    )

@app.route('/account/<subscription_id>')
@auth.require_login
def subscription_view(subscription_id):
    """Renders the subscription details."""
    creds = _get_credentials()
    model = models.get_subscription_details(subscription_id, creds)
    return render_template(
        'subscription.html',
        title=subscription_id,
        year=datetime.now().year,
        subscription_id=subscription_id,
        model=model,
    )

@app.route('/account/<subscription_id>/resourcegroups/<resource_group_name>')
@auth.require_login
def resourcegroup_view(subscription_id, resource_group_name):
    """Renders the resource group details."""
    creds = _get_credentials()
    model = models.get_resource_group_details(subscription_id, creds, resource_group_name)
    return render_template(
        'resourcegroup.html',
        title=resource_group_name,
        year=datetime.now().year,
        subscription_id=subscription_id,
        resource_group_name=resource_group_name,
        model=model,
    )

@app.route('/account/<subscription_id>/resourcegroups/<resource_group_name>/vms/<vm_name>')
@auth.require_login
def vm_view(subscription_id, resource_group_name, vm_name):
    """Renders the vm details."""
    creds = _get_credentials()
    model = models.get_vm_details(subscription_id, creds, resource_group_name, vm_name)
    return render_template(
        'vm.html',
        title=vm_name,
        year=datetime.now().year,
        subscription_id=subscription_id,
        resource_group_name=resource_group_name,
        model=model,
    )

@app.route('/account/<subscription_id>/resourcegroups/<resource_group_name>/virtualnetworks/<network_name>')
@auth.require_login
def virtual_network_view(subscription_id, resource_group_name, network_name):
    """Renders the vm details."""
    creds = _get_credentials()
    model = models.get_virtual_network_details(subscription_id, creds, resource_group_name, network_name)
    return render_template(
        'virtual_network.html',
        title=network_name,
        year=datetime.now().year,
        subscription_id=subscription_id,
        resource_group_name=resource_group_name,
        model=model,
    )

@app.route('/account/<subscription_id>/resourcegroups/<resource_group_name>/storageaccounts/<account_name>')
@auth.require_login
def storageaccount_view(subscription_id, resource_group_name, account_name):
    """Renders the storage account details."""
    creds = _get_credentials()
    model = models.get_storage_account_details(subscription_id, creds, resource_group_name, account_name)
    return render_template(
        'storageaccount.html',
        title=account_name,
        year=datetime.now().year,
        subscription_id=subscription_id,
        resource_group_name=resource_group_name,
        model=model,
    )

@app.route('/account/<subscription_id>/resourcegroups/<resource_group_name>/storageaccounts/<account_name>/containers/<container_name>')
@auth.require_login
def storageaccount_container_view(subscription_id, resource_group_name, account_name, container_name):
    """Renders the storage account container details."""
    creds = _get_credentials()
    model = models.get_container_details(subscription_id, creds, resource_group_name, account_name, container_name)
    return render_template(
        'storageaccount_container.html',
        title=container_name,
        year=datetime.now().year,
        subscription_id=subscription_id,
        resource_group_name=resource_group_name,
        account_name=account_name,
        model=model,
    )

@app.route('/account/<subscription_id>/resourcegroups/<resource_group_name>/storageaccounts/<account_name>/queues/<queue_name>')
@auth.require_login
def storageaccount_queue_view(subscription_id, resource_group_name, account_name, queue_name):
    """Renders the storage account queue details."""
    creds = _get_credentials()
    model = models.get_queue_details(subscription_id, creds, resource_group_name, account_name, queue_name)
    return render_template(
        'storageaccount_queue.html',
        title=queue_name,
        year=datetime.now().year,
        subscription_id=subscription_id,
        resource_group_name=resource_group_name,
        account_name=account_name,
        model=model,
    )

@app.route('/account/<subscription_id>/resourcegroups/<resource_group_name>/storageaccounts/<account_name>/tables/<table_name>')
@auth.require_login
def storageaccount_table_view(subscription_id, resource_group_name, account_name, table_name):
    """Renders the storage account table details."""
    creds = _get_credentials()
    model = models.get_table_details(subscription_id, creds, resource_group_name, account_name, table_name)
    return render_template(
        'storageaccount_table.html',
        title=table_name,
        year=datetime.now().year,
        subscription_id=subscription_id,
        resource_group_name=resource_group_name,
        account_name=account_name,
        model=model,
    )

@app.route('/account/<subscription_id>/providers/<provider_namespace>/unregister', methods=['POST'])
@auth.require_login
def provider_unregister_post(subscription_id, provider_namespace):
    """Unregister provider request."""
    creds = _get_credentials()
    models.unregister_provider(subscription_id, creds, provider_namespace)
    return redirect(url_for('subscription_view', subscription_id=subscription_id))

@app.route('/account/<subscription_id>/providers/<provider_namespace>/register', methods=['POST'])
@auth.require_login
def provider_register_post(subscription_id, provider_namespace):
    """Register provider request."""
    creds = _get_credentials()
    models.register_provider(subscription_id, creds, provider_namespace)
    return redirect(url_for('subscription_view', subscription_id=subscription_id))


##############################################################################
# REST API

# TODO: make better URLs for these, move some form params to URL query params

def get_data_from_response(result):
    status_code = result.status_code
    if status_code == 409:
        msg = "Failed"
    elif status_code == 500:
        msg = "InProgress"
    elif status_code == 202:
        msg = "InProgress"
    elif status_code == 200:
        msg = "Succeeded"
    else:
        msg = ""
    return {
        'code': status_code,
        'status': msg,
    }

@app.route('/createstorageaccount', methods=['POST'])
@auth.require_login
def storageaccount_create_rest_post():
    subscription_id = request.form['subscriptionid']
    resource_group_name = request.form['resourcegroup']
    account_name = request.form['name']
    account_location = request.form['location']
    account_type = request.form['accounttype']
    creds = _get_credentials()
    try:
        result = models.create_storage_account(subscription_id, creds, resource_group_name, account_name, account_location, account_type)
        data = get_data_from_response(result)
        data['operationStatusLink'] = result.headers['Location']
    except CloudError as ex:
        import json
        error_dict = json.loads(ex.error.decode('utf-8'))
        data = {
            'operationStatusLink': None,
            'code': ex.status_code,
            'status': error_dict['error']['message'],
        }
    except IndexError as ex:
        data = {
            'operationStatusLink': None,
            'code': 400,
            'status': str(ex),
        }
    except ValueError as ex:
        data = {
            'operationStatusLink': None,
            'code': 400,
            'status': str(ex),
        }
    return jsonify(data)


@app.route('/deletestorageaccount', methods=['POST'])
@auth.require_login
def storageaccount_delete_rest_post():
    subscription_id = request.form['subscriptionid']
    resource_group_name = request.form['resourcegroup']
    account_name = request.form['name']
    creds = _get_credentials()
    result = models.delete_storage_account(subscription_id, creds, resource_group_name, account_name)
    return '', 200

@app.route('/getcreatestorageaccountstatus', methods=['GET'])
@auth.require_login
def storageaccount_create_status_rest_get():
    subscription_id = request.args.get('subscriptionid')
    link = request.args.get('operationStatusLink')
    creds = _get_credentials()
    result = models.get_create_storage_account_status(subscription_id, creds, link)
    data = get_data_from_response(result)
    return jsonify(data)

@app.route('/getmoretableentities', methods=['GET'])
@auth.require_login
def storageaccount_table_entities_rest_get():
    subscription_id = request.args.get('subscriptionid')
    resource_group_name = request.args.get('resourceGroupName')
    account_name = request.args.get('accountName')
    table_name = request.args.get('tableName')
    next_partition_key = request.args.get('nextPartitionKey')
    next_row_key = request.args.get('nextRowKey')
    creds = _get_credentials()

    model = models.get_table_details(subscription_id, creds, resource_group_name, account_name, table_name, next_partition_key, next_row_key)

    result_entities = []
    for entity in model.entities:
        result_item = {}
        for field in model.custom_fields.union(['PartitionKey', 'RowKey', 'Timestamp']):
            val = getattr(entity, field, '')
            result_item[field] = val
        result_entities.append(result_item)
    result = {'entities':result_entities}
    if hasattr(model.entities, 'x_ms_continuation'):
        result['nextPartitionKey'] = model.entities.x_ms_continuation['NextPartitionKey']
        result['nextRowKey'] = model.entities.x_ms_continuation['NextRowKey']
    else:
        result['nextPartitionKey'] = None
        result['nextRowKey'] = None
    js = jsonify(result)
    return js

##############################################################################
# Helpers

def _get_credentials():
    auth_token = _get_auth_token()
    from msrest.authentication import BasicTokenAuthentication
    return BasicTokenAuthentication(
        token = {
            'access_token':auth_token
        }
    )

def _get_auth_token():
    token = session.get('accessToken')
    if token is None:
        abort(401)
    return token
