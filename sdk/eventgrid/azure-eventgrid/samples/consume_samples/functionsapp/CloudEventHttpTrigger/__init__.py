import logging

import azure.functions as func
#from azure.eventgrid import EventGridConsumer

validationType = "Microsoft.EventGrid.SubscriptionValidationEvent"

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    try:
        req_body = req.get_json()
        if type(req_body) == list:  # if list then event grid events
            for event in req_body:
                if event["eventType"] == validationType:    # validate event grid events
                    code = event["data"]["validationCode"]
                    validation_response = str({"validationResponse": code})
                    return func.HttpResponse(
                        body=validation_response,
                        status_code=200
                    )
                else:
                    return func.HttpResponse(
                        "Event with body: {}".format(str(event)),
                        status_code=200
                    )
        else:   # cloud events sent one at a time
            event = req_body
            if 'specversion' in event.keys() and req.method=="OPTIONS":   # validate cloud events
                #if event["type"] == validationType:
                #    code = event["data"]["validationCode"]
                #    validation_response = str({"validationResponse": code})
                return func.HttpResponse(
                    headers={'Webhook-Allowed-Origin': 'eventgrid.azure.net'},
                #    body=validation_response,
                    status_code=200
                )
            else:
                return func.HttpResponse(
                    "Event with body: {}".format(event),
                    status_code=200
                )
    except ValueError:
        return func.HttpResponse(
             "This HTTP triggered function request did not have a valid body: {}".format(req.get_body()),
             status_code=200
        )
