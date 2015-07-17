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
from azure.common import SubscriptionCloudCredentials, AzureException

app.secret_key = auth.app_creds.SESSION_SECRET

@app.route('/')
@app.route('/home')
def home():
    """Renders the home page."""
    return render_template(
        'index.html',
        title='Home Page',
        year=datetime.now().year,
    )

@app.route('/login')
def login():
    """Renders the login page."""
    redirect_uri = request.values.get(
        'redirect_uri',
        url_for('subscriptions', _external=True),
    )
    return render_template(
        'login.html',
        title='Login',
        year=datetime.now().year,
        message='Your login page.',
        redirect_uri=redirect_uri,
    )

@app.route('/logout', methods=['POST'])
def logout():
    auth.clear_session_token()
    return redirect(url_for('home'))

@app.route('/loginredirect')
def loginredirect():
    """Redirects to Azure login page."""
    redirect_uri = request.values.get('redirect_uri')
    session_auth_state = auth.unique_auth_state()
    session['authstate'] = session_auth_state
    session['redirecturiafterauthorized'] = redirect_uri
    auth_url = auth.create_authorization_url(session_auth_state)
    return redirect(auth_url)

@app.route('/authorized')
def authorized():
    """Renders the authorized page."""
    session_auth_state = session.get('authstate')
    auth_code = request.args.get('code')
    auth_state = request.args.get('state')
    if session_auth_state != auth_state:
        abort(401)

    redirect_uri = session.get('redirecturiafterauthorized')

    auth.clear_session_token()
    token_response = auth.get_tokens(auth_code)
    auth.set_session_token_response(token_response)

    if redirect_uri:
        return redirect(redirect_uri)

    return render_template(
        'authorized.html',
        title='Authorized',
        year=datetime.now().year,
        message='You now have an access token and refresh token.',
        adal_response=json.dumps(token_response, indent=4),
    )

@app.route('/contact')
def contact():
    """Renders the contact page."""
    return render_template(
        'contact.html',
        title='Contact',
        year=datetime.now().year,
        message='Your contact page.'
    )

@app.route('/subscriptions')
@auth.require_login
def subscriptions():
    """Renders the subscription list."""
    subs = models.get_subscriptions(get_auth_token())
    tenants = models.get_tenants(get_auth_token())
    for tenant in tenants:
        pass

    return render_template(
        'subscription_list.html',
        title='Subscriptions',
        year=datetime.now().year,
        subscriptions=subs,
        tenants=tenants,
    )

@app.route('/subscriptions/<subscription_id>/resourcegroups')
@auth.require_login
def resourcegroups(subscription_id):
    """Renders the subscription details."""
    creds = get_credentials(subscription_id)
    groups = models.get_resource_groups(creds)
    providers = models.get_providers(creds)
    return render_template(
        'subscription_details.html',
        title=subscription_id,
        year=datetime.now().year,
        subscription_id=creds.subscription_id,
        groups=groups,
        providers=providers,
    )

@app.route('/subscriptions/<subscription_id>/resourcegroups/<resource_group_name>')
@auth.require_login
def resourcegroup(subscription_id, resource_group_name):
    """Renders the resource group details."""
    creds = get_credentials(subscription_id)
    accounts = models.get_storage_accounts_for_resource_group(creds, resource_group_name)
    account_locations = models.get_storage_accounts_locations(creds)
    return render_template(
        'resourcegroup_details.html',
        title=resource_group_name,
        year=datetime.now().year,
        subscription_id=creds.subscription_id,
        accounts=accounts,
        locations=account_locations,
        resource_group_name=resource_group_name,
    )

@app.route('/createstorageaccount', methods=['POST'])
@auth.require_login
def createstorageaccount():
    subscription_id = request.form['subscriptionid']
    resource_group_name = request.form['resourcegroup']
    account_name = request.form['name']
    account_location = request.form['location']
    account_type = request.form['accounttype']
    creds = get_credentials(subscription_id)
    try:
        result = models.create_storage_account(creds, resource_group_name, account_name, account_location, account_type)
        data = {
            'operationStatusLink': result.operation_status_link,
            'code': result.status_code,
            'status': result.status,
        }
    except AzureException as ex:
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
def deletestorageaccount():
    subscription_id = request.form['subscriptionid']
    resource_group_name = request.form['resourcegroup']
    account_name = request.form['name']
    creds = get_credentials(subscription_id)
    result = models.delete_storage_account(creds, resource_group_name, account_name)
    return '', 200

@app.route('/getcreatestorageaccountstatus', methods=['GET'])
@auth.require_login
def getcreatestorageaccountstatus():
    subscription_id = request.args.get('subscriptionid')
    link = request.args.get('operationStatusLink')
    creds = get_credentials(subscription_id)
    result = models.get_create_storage_account_status(creds, link)
    code = result.status_code
    msg = result.status
    data = {
        'code': result.status_code,
        'status': result.status,
    }
    return jsonify(data)

@app.route('/getmoretableentities', methods=['GET'])
@auth.require_login
def getmoretableentities():
    subscription_id = request.args.get('subscriptionid')
    resource_group_name = request.args.get('resourceGroupName')
    account_name = request.args.get('accountName')
    table_name = request.args.get('tableName')
    next_partition_key = request.args.get('nextPartitionKey')
    next_row_key = request.args.get('nextRowKey')
    creds = get_credentials(subscription_id)
    keys = models.get_storage_account_keys(creds, resource_group_name, account_name)
    entities = models.get_table_entities(account_name, keys.key1, table_name, next_partition_key, next_row_key)
    custom_fields = models.get_entities_custom_fields(entities)
    result_entities = []
    for entity in entities:
        result_item = {}
        for field in custom_fields.union(['PartitionKey', 'RowKey', 'Timestamp']):
            val = getattr(entity, field, '')
            result_item[field] = val
        result_entities.append(result_item)
    result = {'entities':result_entities}
    if hasattr(entities, 'x_ms_continuation'):
        result['nextPartitionKey'] = entities.x_ms_continuation['NextPartitionKey']
        result['nextRowKey'] = entities.x_ms_continuation['NextRowKey']
    else:
        result['nextPartitionKey'] = None
        result['nextRowKey'] = None
    js = jsonify(result)
    return js

@app.route('/subscriptions/<subscription_id>/resourcegroups/<resource_group_name>/storageaccounts/<account_name>')
@auth.require_login
def storageaccount(subscription_id, resource_group_name, account_name):
    """Renders the storage account details."""
    creds = get_credentials(subscription_id)
    properties, keys, blob_containers, tables, queues, blob_service_properties, table_service_properties, queue_service_properties = models.get_storage_account_details(creds, resource_group_name, account_name)
    return render_template(
        'storageaccount_details.html',
        title=account_name,
        year=datetime.now().year,
        subscription_id=creds.subscription_id,
        account_props=properties,
        account_keys=keys,
        blob_containers=blob_containers,
        tables=tables,
        queues=queues,
        blob_service_properties=blob_service_properties,
        table_service_properties=table_service_properties,
        queue_service_properties=queue_service_properties,
        resource_group_name=resource_group_name,
    )

@app.route('/subscriptions/<subscription_id>/resourcegroups/<resource_group_name>/storageaccounts/<account_name>/containers/<container_name>')
@auth.require_login
def storageaccountcontainer(subscription_id, resource_group_name, account_name, container_name):
    """Renders the storage account container details."""
    creds = get_credentials(subscription_id)
    keys = models.get_storage_account_keys(creds, resource_group_name, account_name)
    blobs, sas_expiry = models.get_blobs(account_name, keys.key1, container_name)
    return render_template(
        'storageaccountcontainer_details.html',
        title=container_name,
        year=datetime.now().year,
        subscription_id=creds.subscription_id,
        blobs=blobs,
        resource_group_name=resource_group_name,
        account_name=account_name,
        container_name=container_name,
        sas_expiry=sas_expiry,
    )

@app.route('/subscriptions/<subscription_id>/resourcegroups/<resource_group_name>/storageaccounts/<account_name>/queues/<queue_name>')
@auth.require_login
def storageaccountqueue(subscription_id, resource_group_name, account_name, queue_name):
    """Renders the storage account queue details."""
    creds = get_credentials(subscription_id)
    keys = models.get_storage_account_keys(creds, resource_group_name, account_name)
    metadata, messages = models.get_queue_details(account_name, keys.key1, queue_name)
    return render_template(
        'storageaccountqueue_details.html',
        title=queue_name,
        year=datetime.now().year,
        subscription_id=creds.subscription_id,
        resource_group_name=resource_group_name,
        account_name=account_name,
        queue_name=queue_name,
        metadata=metadata,
        messages=messages,
    )

@app.route('/subscriptions/<subscription_id>/resourcegroups/<resource_group_name>/storageaccounts/<account_name>/tables/<table_name>')
@auth.require_login
def storageaccounttable(subscription_id, resource_group_name, account_name, table_name):
    """Renders the storage account queue details."""
    creds = get_credentials(subscription_id)
    keys = models.get_storage_account_keys(creds, resource_group_name, account_name)
    entities = models.get_table_entities(account_name, keys.key1, table_name)
    custom_fields = models.get_entities_custom_fields(entities)
    return render_template(
        'storageaccounttable_details.html',
        title=table_name,
        year=datetime.now().year,
        subscription_id=creds.subscription_id,
        resource_group_name=resource_group_name,
        account_name=account_name,
        table_name=table_name,
        entities=entities,
        custom_fields=custom_fields,
    )

@app.route('/subscriptions/<subscription_id>/providers/<provider_namespace>/unregister', methods=['POST'])
@auth.require_login
def providerunregister(subscription_id, provider_namespace):
    """Renders the storage account container details."""
    creds = get_credentials(subscription_id)
    models.unregister_provider(creds, provider_namespace)
    return redirect(url_for('resourcegroups', subscription_id=subscription_id))

@app.route('/subscriptions/<subscription_id>/providers/<provider_namespace>/register', methods=['POST'])
@auth.require_login
def providerregister(subscription_id, provider_namespace):
    """Renders the storage account container details."""
    creds = get_credentials(subscription_id)
    models.register_provider(creds, provider_namespace)
    return redirect(url_for('resourcegroups', subscription_id=subscription_id))

def get_credentials(subscription_id):
    auth_token = get_auth_token()
    return SubscriptionCloudCredentials(subscription_id, auth_token)

def get_auth_token():
    token = session.get('accessToken')
    if token is None:
        abort(401)
    return token
