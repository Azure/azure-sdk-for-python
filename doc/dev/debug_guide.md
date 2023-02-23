# Debug

This guide is to help Python SDK users to get the process about how SDK call REST api

(1) Copy the following code in your .py file
```python
import sys
import logging

logger = logging.getLogger('')
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(stream=sys.stdout, )
logger.addHandler(handler)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
```

![Position example](./debug_guide_position.png "Position example")

nit: the following code has same effect:
```python
import sys
import logging

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    stream=sys.stdout)
```
(2) Run your .py program and you could find the log info in screen. It is convenient to get the process about how SDK call REST api:

![example](./debug_guide_example.png "example")
