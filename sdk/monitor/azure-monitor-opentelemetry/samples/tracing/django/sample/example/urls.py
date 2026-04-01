# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License in the project root for
# license information.
# --------------------------------------------------------------------------

from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("exception", views.exception, name="exception"),
]
