# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# -----------------------------------------------------------------------------------

FROM torosent/python-qpid-proton
RUN pip3 install lxml beautifulsoup4 azure
COPY . /azure-event-hubs-python
WORKDIR /azure-event-hubs-python
RUN python3 setup.py install && pip3 install -e .
# CMD python3 playground.py
CMD python3 eventprocessorhost/tests/test_eph.py