import json

g_cfg = {}


def LoadConfig(file_path):
    global g_cfg
    with open(file_path, 'r') as f:
        g_cfg = json.load(f)
    g_cfg['host'] = 'localhost'


