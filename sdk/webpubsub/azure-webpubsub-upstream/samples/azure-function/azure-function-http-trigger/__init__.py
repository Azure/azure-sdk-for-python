'''
 # @ Author: Terence Fan
 # @ Create Time: 2021-10-26 11:56:42
 # @ Modified by: Terence Fan
 # @ Modified time: 2021-10-26 11:56:47
 # @ Description:
 '''


import azure.functions as func

from flask import Flask

from azure.messaging.webpubsub.upstream import (
    EventHandler,
    AccessKeyValidator,
)

from azure.messaging.webpubsub.upstream.exceptions import (
    HeaderNotFoundError,
)


CONNECTION_STRING = "Endpoint=https://foobar.webpubsub.azure.com;AccessKey=KgSuDSOjE0dzipErsHk01KnQXQ5iEAlDC3ypY2nO3Vk=;Version=1.0;"


def handle_connect(context):
    return {}


def handle_exception(e):
    if isinstance(e, HeaderNotFoundError):
        print(e.key)
    print(type(e))


handler = EventHandler(
    handle_connect=handle_connect,
    handle_exception=handle_exception,
    request_validator=AccessKeyValidator(CONNECTION_STRING),
)

flask = Flask(__name__)

app = handler.wrap(flask.wsgi_app, "/api/azure-function-http-trigger")

main = func.WsgiMiddleware(app).main