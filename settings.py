import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

LOG_PATH = "/home/pi/rglog"
HOST = "localhost"
HTTP_PORT = 8000
URL_PREFIX = "/rxg/"
REDIS = {
    "host": "localhost",
    "port": 21999
}
BIZ_DB = {
    "path": "/home/pi/rxg_biz.db3"
}
LOG_DB = {
    "path": "/home/pi/rxg_log.db3",
    "ttl": 3*86400
}
