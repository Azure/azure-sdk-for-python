from cgi import test
from datetime import date, datetime
from tracemalloc import start
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv
# import azure.analytics.loadtestservice as loadtest
import azure.developer.loadtestservice as loadtest
import json
import time
from azure.core.exceptions import HttpResponseError

load_dotenv()

# Preparing body content for Creation/updation
dic_file = {}
f= open("SampleApp.jmx","rb")
dic_file["file"]=f 
dic_test={"resourceId":"/subscriptions/7c71b563-0dc0-4bc0-bcf6-06f8f0516c7a/resourceGroups/yashika-rg/providers/Microsoft.LoadTestService/loadtests/loadtestsdk",
        "testId":"a011890b-0201-004d-010d-1200d888aa002","description":"","displayName":"nivedit-15",
        "loadTestConfig":{"engineSize":"m","engineInstances":1,"splitAllCSVs":False},"secrets":{},
        "environmentVariables":{},"passFailCriteria":{"passFailMetrics":{}},"keyvaultReferenceIdentityType":"SystemAssigned",
        "keyvaultReferenceIdentityId":None}
dic_app={"name":"app_component","testId":"a011890b-0201-004d-010d-1200d888aa002",
        "value":{"/subscriptions/7c71b563-0dc0-4bc0-bcf6-06f8f0516c7a/resourceGroups/App-Service-Sample-Demo-rg/providers/Microsoft.Web/sites/App-Service-Sample-Demo":
        {"resourceId":"/subscriptions/7c71b563-0dc0-4bc0-bcf6-06f8f0516c7a/resourceGroups/App-Service-Sample-Demo-rg/providers/Microsoft.Web/sites/App-Service-Sample-Demo",
        "resourceName": "App-Service-Sample-Demo","resourceType": "Microsoft.Web/sites",
        "subscriptionId":"7c71b563-0dc0-4bc0-bcf6-06f8f0516c7a"}}}
dic_testrun= {"testId":"a011890b-0201-004d-010d-1200d888aa002", "displayName":"python_test_run_demo",
            "requestSamplers":[],"errors":[],"percentiles":["90"],"groupByInterval":"5s"}

test_id="a011890b-0201-004d-010d-1200d888aa002"
file_id="a012b234-1230-ab00-0040-ab12c450008d2"
test_run_id="08673e89-3285-46a1-9c6b-7e5ecba390002"
app_component="01730263-6671-4216-b283-8b28ed9530002"


#Creating client through AAD
client=loadtest.LoadTestClient(credential=DefaultAzureCredential(), endpoint="eccdc9b7-7603-402b-879d-bde2b637db56.eus.cnt-prod.loadtesting.azure.com")


# Creating load test
try:  
    result = client.test.create_or_update_test(test_id, dic_test)
    print(result)
except HttpResponseError as e:
    print('Failed to process the request: {}'.format(e.response.json()))

# Uploading the test file
try: 
    result=client.test.upload_test_file(test_id,file_id,dic_file)
    print(result)
except HttpResponseError as e:
    print('Failed to send JSON message: {}'.format(e.response.json()))

# Checking the validation status
try: 
    result=client.test.get_test_file(test_id,file_id)
    start_time=time.time()
    while time.time() - start_time < 300:
        result=client.test.get_test_file(test_id,file_id)
        if result['validationStatus']=='VALIDATION_SUCCESS':
            break
        else:
            time.sleep(3)
    print(result)
except HttpResponseError as e:
    print('Failed to send JSON message: {}'.format(e.response.json()))

# Creating app component
try: 
    result=client.app_component.create_or_update_app_components(app_component,dic_app)
    print(result)
except HttpResponseError as e:
    print('Failed to send JSON message: {}'.format(e.response.json()))

#Creating the test run
try: 
    result=client.test_run.create_and_update_test(test_run_id,dic_testrun)
    print(result)
except HttpResponseError as e:
    print('Failed to send JSON message: {}'.format(e.response.json()))

#Checking the test run status and printing metrics
try: 
    start_time=time.time()
    while time.time() - start_time < 300:
        result=client.test_run.get_test_run(test_run_id)
        if result['status'] == "DONE" or result['status'] == "CANCELLED" or result['status'] == "FAILED":
            break
        else:
            time.sleep(10)
    print(result['testRunStatistics'])
except HttpResponseError as e:
    print('Failed to send JSON message: {}'.format(e.response.json()))