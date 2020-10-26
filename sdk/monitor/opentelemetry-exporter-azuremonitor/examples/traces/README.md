
## Installation

```sh
$ pip install opentelemetry-azure-monitor
```

## Run the Applications

### Trace

* Update the code in trace.py to use your `INSTRUMENTATION_KEY`

* Run the sample

```sh
$ # from this directory
$ python trace.py
```

### Request

* Update the code in request.py to use your `INSTRUMENTATION_KEY`

* Run the sample

```sh
$ pip install opentelemetry-ext-http-requests
$ # from this directory
$ python request.py
```

### Server

* Update the code in server.py to use your `INSTRUMENTATION_KEY`

* Run the sample

```sh
$ pip install opentelemetry-ext-http-requests
$ pip install opentelemetry-ext-wsgi
$ # from this directory
$ python server.py
```

* Open http://localhost:8080/ 


## Explore the data

After running the applications, data would be available in [Azure](
https://docs.microsoft.com/en-us/azure/azure-monitor/app/app-insights-overview#where-do-i-see-my-telemetry)
