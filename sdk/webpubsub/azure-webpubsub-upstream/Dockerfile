ARG PythonVersion=${PythonVersion}
FROM python:$PythonVersion

WORKDIR /usr/src/sdk

COPY . .

RUN pip install --upgrade pip
RUN python setup.py develop
RUN pip install -r dev_requirements.txt
RUN pip install pytest

CMD ["pytest", "tests"]