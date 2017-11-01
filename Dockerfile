FROM torosent/qpid

RUN git clone -b develop --single-branch https://github.com/Azure/azure-event-hubs-python.git

WORKDIR /azure-event-hubs-python
RUN python3 setup.py install && pip3 install -e . && pip3 install lxml beautifulsoup4 azure
