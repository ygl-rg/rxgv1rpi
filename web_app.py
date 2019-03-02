import cyclone.web as cyclone_web
import apis_http
import rxg_consts


def GetApi():
    return [(rxg_consts.Node_URLs.API_ZB_DEVICE_ADM, apis_http.ZbDeviceAdm),
            (rxg_consts.Node_URLs.API_SYS_CFG, apis_http.SysCfg),
            (rxg_consts.Node_URLs.API_ZB_MODULE_ADM, apis_http.ZbModuleAdm),
            (rxg_consts.Node_URLs.API_EM, apis_http.EnvMonitor)
            ]


class App(cyclone_web.Application):
    def __init__(self):
        cyclone_web.Application.__init__(self, GetApi(), gzip=True)
