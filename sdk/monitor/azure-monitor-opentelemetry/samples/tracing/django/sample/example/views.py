# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License in the project root for
# license information.
# --------------------------------------------------------------------------

from django.http import HttpResponse


# Requests sent to the django application will be automatically captured
def index(request):
    return HttpResponse("Hello, world.")


# Exceptions that are raised within the request are automatically captured
def exception(request):
    raise Exception("Exception was raised.")
