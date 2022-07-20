# Integration Testing

## Running

Once you have set up your Azure Resources and your `.env` file, from this directory, run

```python
python -h http.server 8000
```

(You can use any other port). Then, from a Chromium-based browser such as Edge, go to [`http://localhost:8000/`](http://localhost:8000/) and the tests will be run in the browser. Dev tip: keep your browser's devtools open.

## Adding tests

Add tests in `browser_test.py`. I couldn't get `pytest` or `unittest` to cooperate with me, so I made my own little async testing framework (`async_test.py`). If you are creating new files to test or new packages, update the `TEST_FILES` and `PACKAGES` variables in `index.html`, import the test case, and run it.

## Sensitive values

To run the tests, you need a `.env` folder in this directory with your sensitive values.
see `example-env`. You can then access the values as environment variables using `os.getenv`. You will
need to have your `textanalytics` key and endpoint as well as your Blob Storage key and url.

## Dependencies

All all packages listed in `requirements.txt` will be available in the testing environment.
 
## Azure Resources

You need your own Text Analytics and Blob Storage accounts to run these tests. Blob storage requirest some additional configuration to work. To set up Blob Storage, navigate to your storage client homepage and go to the `Resource Sharing (CORS)` tab. Create a rule with the following values

| Allowed origins | Allowed methods | Allowed headers | Exposed headers | Max age |
|-----------------|-----------------|-----------------|-----------------|---------|
| `*`             | All             | `*`             | See below       | `3600`  |

For exposed headers, put

> Server,Content-Range,ETag,Last-Modified,Accept-Ranges,x-ms-*
