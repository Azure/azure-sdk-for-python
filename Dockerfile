FROM torosent/python-qpid-proton

RUN pip3 install lxml beautifulsoup4 azure

COPY . /azure-event-hubs-python

WORKDIR /azure-event-hubs-python

RUN python3 setup.py install && pip3 install -e .

CMD python3 eventhubsprocessor/tests/test_eph.py