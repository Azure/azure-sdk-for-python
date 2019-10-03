# --------------------------------------------------------------------------
#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
# The MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the ""Software""), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED *AS IS*, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#
# --------------------------------------------------------------------------

import logging
from .pipeline import Pipeline
from .pipeline.transport.base import PipelineClientBase
from .pipeline.policies import ContentDecodePolicy
from .pipeline.transport import RequestsTransport
from .pipeline.policies.distributed_tracing import DistributedTracingPolicy

try:
    from typing import TYPE_CHECKING
except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
    from typing import (
        List,
        Any,
        Dict,
        Union,
        IO,
        Tuple,
        Optional,
        Callable,
        Iterator,
        cast,
    )  # pylint: disable=unused-import

_LOGGER = logging.getLogger(__name__)


class PipelineClient(PipelineClientBase):
    """Service client core methods.

    Builds a Pipeline client.

    :param str base_url: URL for the request.
    :param config: Service configuration. This is a required parameter.
    :type config: ~azure.core.Configuration
    :param kwargs: keyword arguments
    :return: A pipeline object.
    :rtype: ~azure.core.pipeline.Pipeline

    **Keyword arguments:**

    *pipeline* - A Pipeline object. If omitted, a Pipeline object is created and returned.

    *policies* - A list of policies object. If omitted, the standard policies of the configuration object is used.

    *transport* - The HTTP Transport instance. If omitted, RequestsTransport is used for synchronous transport.

    .. admonition:: Example:

        .. literalinclude:: ../examples/test_example_sync.py
            :start-after: [START build_pipeline_client]
            :end-before: [END build_pipeline_client]
            :language: python
            :dedent: 4
            :caption: Builds the pipeline client.
    """

    def __init__(self, base_url, config, **kwargs):
        super(PipelineClient, self).__init__(base_url)
        if config is None:
            raise ValueError("Config is a required parameter")
        self._config = config
        self._base_url = base_url
        if kwargs.get("pipeline"):
            self._pipeline = kwargs["pipeline"]
        else:
            self._pipeline = self._build_pipeline(config, **kwargs)

    def __enter__(self):
        self._pipeline.__enter__()
        return self

    def __exit__(self, *exc_details):
        self._pipeline.__exit__(*exc_details)

    def close(self):
        self.__exit__()

    def _build_pipeline(self, config, **kwargs): # pylint: disable=no-self-use
        transport = kwargs.get('transport')
        policies = kwargs.get('policies')

        if policies is None:  # [] is a valid policy list
            policies = [
                config.headers_policy,
                config.user_agent_policy,
                config.authentication_policy,
                ContentDecodePolicy(),
                config.redirect_policy,
                config.retry_policy,
                config.custom_hook_policy,
                config.logging_policy,
                DistributedTracingPolicy(),
            ]

        if not transport:
            transport = RequestsTransport(**kwargs)

        return Pipeline(transport, policies)
