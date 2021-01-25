# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from azure.core.polling import LROPoller, AsyncLROPoller
from azure.core.polling.async_base_polling import AsyncLROBasePolling
from azure.core.polling.base_polling import LROBasePolling

class TextAnalyticsLROPoller(LROPoller):

    @property
    def id(self) -> str:
        return self._polling_method.resource().job_id

    @property
    def created_date_time(self):
        return self._polling_method.created_date_time

    @property
    def expiration_date_time(self):
        return self._polling_method.expiration_date_time

    @property
    def last_update_date_time(self):
        return self._polling_method.last_update_date_time

class AsyncTextAnalyticsLROPoller(AsyncLROPoller):

    @property
    def id(self) -> str:
        return self._polling_method.job_id

    @property
    def created_date_time(self):
        return self._polling_method.created_date_time

    @property
    def expiration_date_time(self):
        return self._polling_method.expiration_date_time

    @property
    def last_update_date_time(self):
        return self._polling_method.last_update_date_time


class TextAnalyticsPollingMethod(LROBasePolling):

    @property
    def created_date_time(self):
        return self.resource().created_date_time

    @property
    def expiration_date_time(self):
        return self.resource().expiration_date_time

    @property
    def last_update_date_time(self):
        return self.resource().last_update_date_time

class AsyncTextAnalyticsPollingMethod(AsyncLROBasePolling):

    @property
    def created_date_time(self):
        return self.resource().created_date_time

    @property
    def expiration_date_time(self):
        return self.resource().expiration_date_time

    @property
    def last_update_date_time(self):
        return self.resource().last_update_date_time
