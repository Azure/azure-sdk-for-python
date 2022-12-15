# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
]
