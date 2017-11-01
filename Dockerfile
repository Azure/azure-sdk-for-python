FROM torosent/qpid

RUN git clone -b EventProcessingHostArchitecture --single-branch https://github.com/CatalystCode/azure-event-hubs-python.git

WORKDIR /azure-event-hubs-python
ADD mock_credentials.py ./eventhubsprocessor/tests
RUN python3 setup.py install && pip3 install -e . && pip3 install lxml beautifulsoup4 azure
