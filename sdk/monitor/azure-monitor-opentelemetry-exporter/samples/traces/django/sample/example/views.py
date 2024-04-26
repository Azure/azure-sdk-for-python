# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
# mypy: disable-error-code="attr-defined"

from django.http import HttpResponse

def index(request):
    return HttpResponse("Hello, world.")
