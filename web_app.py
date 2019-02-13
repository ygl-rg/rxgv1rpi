import os.path as os_path
import cyclone.web as cyclone_web
import rg_lib
import ui_http
import static_tpl_http
import apis_http
import rxg_consts
import g_vars


def GetStaticHandlers(static_path, export_path):
    return [(rg_lib.Cyclone.Dir2Url('imgs'), rg_lib.TempFileHandler, {"path": os_path.join(static_path, 'imgs')}),
            (rg_lib.Cyclone.Dir2Url('jslib'), rg_lib.TempFileHandler, {"path": os_path.join(static_path, 'jslib')}),
            (rg_lib.Cyclone.Dir2Url('js'), rg_lib.TempFileHandler, {"path": os_path.join(static_path, 'js')}),
            (rg_lib.Cyclone.Dir2Url('css'), rg_lib.TempFileHandler, {"path": os_path.join(static_path, 'css')}),
            (rg_lib.Cyclone.Dir2Url('export'), rg_lib.ExcelFileHandler, {"path": export_path})]


def GetStaticTplHandlers():
    return [
        (rg_lib.Cyclone.Dir2Url(g_vars.g_cfg['web']['js_dir']), static_tpl_http.JsHandler),
        (rg_lib.Cyclone.Dir2Url(g_vars.g_cfg['web']['css_dir']), static_tpl_http.CssHandler),
        (rg_lib.Cyclone.Dir2Url(g_vars.g_cfg['web']['template_dir']), static_tpl_http.DojoTplHandler)
    ]


def GetApi():
    return [(rxg_consts.Node_URLs.API_ZB_DEVICE_ADM, apis_http.ZbDeviceAdm),
            (rxg_consts.Node_URLs.API_SYS_CFG, apis_http.SysCfg),
            (rxg_consts.Node_URLs.API_ZB_MODULE_ADM, apis_http.ZbModuleAdm),
            (rxg_consts.Node_URLs.API_EM, apis_http.EnvMonitor)
            ]


def GetAPP():
    return [
        (rxg_consts.Node_URLs.APP_ADM_LOGIN, ui_http.AppAdmLogin),
        (rxg_consts.Node_URLs.APP_EDIT_ZB_DEVICE, ui_http.AppEditZbDevice),
        (rxg_consts.Node_URLs.APP_ADM_ZB_DEVICE, ui_http.AppZbDeviceAdm),
        (rxg_consts.Node_URLs.APP_SYNC_ZB_DEVICE, ui_http.AppSyncZbDevice),
        (rxg_consts.Node_URLs.APP_RECAP_ZB_DEVICE, ui_http.AppRecapZbDevice),
        (rxg_consts.Node_URLs.APP_DEVICE_OP_LOG, ui_http.AppDeviceOpLog),
        (rxg_consts.Node_URLs.APP_DEVICE_OP_ERROR_COUNT, ui_http.AppDeviceOpErrorCount),
        (rxg_consts.Node_URLs.APP_ADM_ZB_MODULE, ui_http.AppZbModuleAdm),
        (rxg_consts.Node_URLs.APP_RESTORE_ZB_MODULE, ui_http.AppRestoreZbModule),
        (rxg_consts.Node_URLs.APP_EM, ui_http.AppEm),
        (rxg_consts.Node_URLs.APP_EM_SENSOR, ui_http.AppEmSensor)
    ]


class App(cyclone_web.Application):
    def __init__(self, static_path, export_path, tpl_path):
        handlers = GetStaticHandlers(static_path, export_path) + GetApi() + GetAPP() + GetStaticTplHandlers()
        cyclone_web.Application.__init__(self, handlers, gzip=True,
                                         template_path=tpl_path)
