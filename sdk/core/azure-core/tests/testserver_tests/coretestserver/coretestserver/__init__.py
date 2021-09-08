# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------

from flask import Flask, Response
from .test_routes import (
    basic_api,
    encoding_api,
    errors_api,
    polling_api,
    streams_api,
    urlencoded_api,
    multipart_api,
    xml_api,
    headers_api,
)

app = Flask(__name__)
app.register_blueprint(basic_api, url_prefix="/basic")
app.register_blueprint(encoding_api, url_prefix="/encoding")
app.register_blueprint(errors_api, url_prefix="/errors")
app.register_blueprint(polling_api, url_prefix="/polling")
app.register_blueprint(streams_api, url_prefix="/streams")
app.register_blueprint(urlencoded_api, url_prefix="/urlencoded")
app.register_blueprint(multipart_api, url_prefix="/multipart")
app.register_blueprint(xml_api, url_prefix="/xml")
app.register_blueprint(headers_api, url_prefix="/headers")

@app.route('/health', methods=['GET'])
def latin_1_charset_utf8():
    return Response(status=200)

if __name__ == "__main__":
    app.run(debug=True)
