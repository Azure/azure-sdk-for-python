# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License in the project root for
# license information.
# --------------------------------------------------------------------------

# mypy: disable-error-code="attr-defined"
import logging
from django.http import HttpResponse


logger = logging.getLogger("app_logger")

def index(request):
    logger.info("index page")
    return HttpResponse("Hello, world.")
