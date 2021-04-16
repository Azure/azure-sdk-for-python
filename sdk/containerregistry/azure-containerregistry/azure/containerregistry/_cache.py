# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from datetime import datetime, timedelta

class ACRCache(object):
    def __init__(self, **kwargs):
        self._tokens = {}
        self.cache_size = kwargs.get("cache_size", 25)
        self.expiry = kwargs.get("token_expiry", 300)  # 5 minute expiry

    def check_refresh_token(self, service):
        # type: (str) -> Union[None, str]
        refresh = self._tokens.get(service)
        if refresh:
            (token, expiry) = refresh
            if datetime.now() - expiry > timedelta(seconds=self.expiry):
                del self._tokens[service]
                return None
        return self._tokens.get(service)

    def set_refresh_token(self, service, token):
        if len(self._tokens) >= self.cache_size:
            self._remove_token()
        self._tokens[service] = (token, datetime.now())

    def _remove_token(self):
        oldest_expiry = None
        service_to_remove = None
        for service, (token, expiry) in self._tokens.items():
            if not oldest_expiry or expiry < oldest_expiry:
                oldest_expiry = expiry
                service_to_remove = service

        del self._tokens[service_to_remove]
