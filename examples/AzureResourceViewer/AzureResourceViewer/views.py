"""
Routes and views for the flask application.
"""

from datetime import datetime
from flask import render_template, redirect, url_for
from . import app
from . import models
from azure.common import SubscriptionCloudCredentials


@app.route('/')
@app.route('/home')
def home():
    """Renders the home page."""
    return render_template(
        'index.html',
        title='Home Page',
        year=datetime.now().year,
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

@app.route('/about')
def about():
    """Renders the about page."""
    return render_template(
        'about.html',
        title='About',
        year=datetime.now().year,
        message='Your application description page.'
    )

@app.route('/subscriptions')
def subscriptions():
    """Renders the subscription list."""
    subs = models.get_subscriptions(get_auth_token())
    return render_template(
        'subscription_list.html',
        title='Subscriptions',
        year=datetime.now().year,
        subscriptions=subs,
    )

@app.route('/subscriptions/<subscription_id>/resourcegroups')
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
def resourcegroup(subscription_id, resource_group_name):
    """Renders the resource group details."""
    creds = get_credentials(subscription_id)
    accounts = models.get_storage_accounts_for_resource_group(creds, resource_group_name)
    return render_template(
        'resourcegroup_details.html',
        title=resource_group_name,
        year=datetime.now().year,
        subscription_id=creds.subscription_id,
        accounts=accounts,
        resource_group_name=resource_group_name,
    )

@app.route('/subscriptions/<subscription_id>/resourcegroups/<resource_group_name>/storageaccounts/<account_name>')
def storageaccount(subscription_id, resource_group_name, account_name):
    """Renders the storage account details."""
    creds = get_credentials(subscription_id)
    properties, keys, blob_containers, tables, queues = models.get_storage_account_details(creds, resource_group_name, account_name)
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
        resource_group_name=resource_group_name,
    )

@app.route('/subscriptions/<subscription_id>/resourcegroups/<resource_group_name>/storageaccounts/<account_name>/containers/<container_name>')
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

@app.route('/subscriptions/<subscription_id>/providers/<provider_namespace>/unregister', methods=['POST'])
def providerunregister(subscription_id, provider_namespace):
    """Renders the storage account container details."""
    creds = get_credentials(subscription_id)
    models.unregister_provider(creds, provider_namespace)
    return redirect(url_for('resourcegroups', subscription_id=subscription_id))

@app.route('/subscriptions/<subscription_id>/providers/<provider_namespace>/register', methods=['POST'])
def providerregister(subscription_id, provider_namespace):
    """Renders the storage account container details."""
    creds = get_credentials(subscription_id)
    models.register_provider(creds, provider_namespace)
    return redirect(url_for('resourcegroups', subscription_id=subscription_id))

def get_credentials(subscription_id):
    auth_token = get_auth_token()
    return SubscriptionCloudCredentials(subscription_id, auth_token)

def get_auth_token():
    import json
    import os.path
    creds_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'credentials_real.json')
    with open(creds_path) as credential_file:
        credential = json.load(credential_file)
        return credential['authorization_header'].split()[1]
