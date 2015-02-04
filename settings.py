# nodes
NODES = [
    {
        "name": "localhost",
        "host": "localhost",
        "port": 9000
    }
]
NODE_POLLING_FREQUENCY = 1
NODES_RELOAD_FREQUENCY = 1

# logging
import logging
LOG_LEVEL = logging.INFO

# database
DATABASE = ""

try:
    from local_settings import *
except ImportError:
    pass
