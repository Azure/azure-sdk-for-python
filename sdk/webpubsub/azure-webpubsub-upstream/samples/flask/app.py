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

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

app.wsgi_app = handler.wrap(app.wsgi_app, "/upstream")