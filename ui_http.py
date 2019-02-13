# -*- coding: utf-8 -*-
from twisted.internet import defer
from twisted.python import log
from cyclone import web as cyclone_web
import rg_lib
import xy_lib
import rxg_consts
import g_vars
import node_models


class UIBase(cyclone_web.RequestHandler):
    async def async_get(self):
        raise NotImplementedError()

    async def async_post(self):
        raise NotImplementedError()

    def get(self):
        return defer.ensureDeferred(self.async_get())

    def post(self):
        return defer.ensureDeferred(self.async_post())


class AppAdmLogin(UIBase):
    def initialize(self, **kwargs):
        self.url_tbl = {'zb_device': rxg_consts.Node_URLs.APP_ADM_ZB_DEVICE,
                        'zb_module': rxg_consts.Node_URLs.APP_ADM_ZB_MODULE}

        self.adm_types = [{'name': 'Zigbee Device|Zigbee设备', 'value': 'zb_device', "checked": 1},
                          {'name': 'Zigbee Module|Zigbee模组', 'value': 'zb_module'}]

    def RenderPage(self, user_lang, hint):
        self.render(rxg_consts.Node_TPL_NAMES.APP_ADM_LOGIN,
                    app_js_dir=g_vars.g_cfg['web']['js_dir'],
                    app_template_dir=g_vars.g_cfg['web']['template_dir'],
                    title="Sys Adm",
                    hint=hint,
                    loginurl=rxg_consts.Node_URLs.APP_ADM_LOGIN,
                    bkgpng=g_vars.g_cfg['web']['login_page_bkg'],
                    user_lang=user_lang,
                    adm_types=self.adm_types)

    async def async_get(self):
        user_lang = self.get_cookie(rxg_consts.Cookies.USERLANG, "eng")
        self.RenderPage(user_lang, '')

    async def async_post(self):
        adm_type = self.get_argument('adm_type', 'zb_device')
        if adm_type in self.url_tbl:
            self.redirect(self.url_tbl[adm_type])
        else:
            raise cyclone_web.HTTPError(404)


class AppEm(UIBase):
    def GetTitle(self):
        return "Elastic Monitoring powered by RoundGIS Lab"

    def GetLabel(self):
        return {
            "en": {"open": "turn on", "close": "turn off", "open_duration_desc": "15-9999 seconds",
                   'goto': 'env data'},
            "zh-cn": {"open": "打开", "close": "关闭", "open_duration_desc": "15-9999秒",
                      'goto': '环境数据'}
        }

    async def handlePage_(self):
        ulang = self.get_cookie(rxg_consts.Cookies.USERLANG, "en")
        label_tbl = self.GetLabel()[ulang]
        self.render(rxg_consts.Node_TPL_NAMES.APP_EM,
                    app_js_dir=g_vars.g_cfg['web']['js_dir'],
                    app_css_dir=g_vars.g_cfg['web']['css_dir'],
                    app_template_dir=g_vars.g_cfg['web']['template_dir'],
                    title=self.GetTitle(),
                    user_lang=ulang,
                    open_valve_label=label_tbl['open'],
                    close_valve_label=label_tbl['close'],
                    em_sensor_url=rxg_consts.Node_URLs.APP_EM_SENSOR[1:],
                    goto_label=label_tbl['goto'])

    async def async_get(self):
        await self.handlePage_()


class AppEmSensor(UIBase):
    def GetTitle(self):
        return "Elastic Sensor powered by RoundGIS Lab"

    def GetLabel(self):
        return {
            "en": {'goto': 'env ctrl', 'sample': 'sample'},
            "zh-cn": {'goto': '环境控制', 'sample': '采样'}
        }

    def GetSampleCountTbls(self):
        return [
            {"label": 10, 'value': 10},
            {"label": 20, "value": 20},
            {"label": 30, "value": 30, 'selected': True},
            {"label": 60, "value": 60},
            {"label": 120, "value": 120},
            {"label": 180, "value": 180}
        ]

    async def handlePage_(self):
        ulang = self.get_cookie(rxg_consts.Cookies.USERLANG, "en")
        label_tbl = self.GetLabel()[ulang]
        self.render(rxg_consts.Node_TPL_NAMES.APP_EM_SENSOR,
                    app_js_dir=g_vars.g_cfg['web']['js_dir'],
                    app_css_dir=g_vars.g_cfg['web']['css_dir'],
                    app_template_dir=g_vars.g_cfg['web']['template_dir'],
                    title=self.GetTitle(),
                    user_lang=ulang,
                    samaple_count_tbls=self.GetSampleCountTbls(),
                    em_url=rxg_consts.Node_URLs.APP_EM[1:],
                    goto_label=label_tbl['goto'],
                    sample_label=label_tbl['sample'])

    async def async_get(self):
        await self.handlePage_()


class AppEditZbDevice(UIBase):
    def GetDeviceNoTbls(self):
        return [{'label': i, 'value': i} for i in xy_lib.DeviceNo.LIST]

    async def async_get(self):
        edit_mode = self.get_argument("edit_mode")
        if edit_mode == "edit":
            deviceid = self.get_argument("deviceid")
            self.render(rxg_consts.Node_TPL_NAMES.APP_EDIT_ZB_DEVICE,
                        app_js_dir=g_vars.g_cfg['web']['js_dir'],
                        app_css_dir=g_vars.g_cfg['web']['css_dir'],
                        app_template_dir=g_vars.g_cfg['web']['template_dir'],
                        title="Edit Zigbee Device",
                        edit_mode=edit_mode, deviceid=deviceid,
                        device_no_tbls=self.GetDeviceNoTbls())
        else:
            raise cyclone_web.HTTPError(404, "zigbee device edit mode incorrect")


class AppZbDeviceAdm(UIBase):
    def GetTitle(self):
        return "Zigbee Device Adm powered by RoundGIS Lab"

    async def async_get(self):
        self.render(rxg_consts.Node_TPL_NAMES.APP_ADM_ZB_DEVICE,
                    app_js_dir=g_vars.g_cfg['web']['js_dir'],
                    app_css_dir=g_vars.g_cfg['web']['css_dir'],
                    app_template_dir=g_vars.g_cfg['web']['template_dir'],
                    title=self.GetTitle(),
                    edit_zb_dev_url=rxg_consts.Node_URLs.APP_EDIT_ZB_DEVICE[1:],
                    recap_zb_dev_url=rxg_consts.Node_URLs.APP_RECAP_ZB_DEVICE[1:],
                    op_log_url=rxg_consts.Node_URLs.APP_DEVICE_OP_LOG[1:],
                    op_error_count_url=rxg_consts.Node_URLs.APP_DEVICE_OP_ERROR_COUNT[1:],
                    zb_module_adm_url=rxg_consts.Node_URLs.APP_ADM_ZB_MODULE[1:])


class AppSyncZbDevice(UIBase):
    def GetTitle(self):
        return "Sync Zigbee Device powered by RoundGIS Lab"

    async def async_get(self):
        moduleid = self.get_argument("moduleid")
        self.render(rxg_consts.Node_TPL_NAMES.APP_SYNC_ZB_DEVICE,
                    app_js_dir=g_vars.g_cfg['web']['js_dir'],
                    app_css_dir=g_vars.g_cfg['web']['css_dir'],
                    app_template_dir=g_vars.g_cfg['web']['template_dir'],
                    title=self.GetTitle(),
                    moduleid=moduleid)


class AppRecapZbDevice(UIBase):
    def GetTitle(self):
        return "Recap Zigbee Device powered by RoundGIS Lab"

    def GetDeviceNoTbls(self):
        return [{'label': i, 'value': i} for i in xy_lib.DeviceNo.LIST]

    async def async_get(self):
        self.render(rxg_consts.Node_TPL_NAMES.APP_RECAP_ZB_DEVICE,
                    app_js_dir=g_vars.g_cfg['web']['js_dir'],
                    app_css_dir=g_vars.g_cfg['web']['css_dir'],
                    app_template_dir=g_vars.g_cfg['web']['template_dir'],
                    title=self.GetTitle(),
                    device_no_tbls=self.GetDeviceNoTbls())


class AppDeviceOpLog(UIBase):
    async def async_get(self):
        deviceid = self.get_argument("deviceid")
        self.render(rxg_consts.Node_TPL_NAMES.APP_DEVICE_OP_LOG,
                    app_js_dir=g_vars.g_cfg['web']['js_dir'],
                    app_css_dir=g_vars.g_cfg['web']['css_dir'],
                    app_template_dir=g_vars.g_cfg['web']['template_dir'],
                    title="Device Op Log",
                    deviceid=deviceid)


class AppDeviceOpErrorCount(UIBase):
    async def async_get(self):
        self.render(rxg_consts.Node_TPL_NAMES.APP_DEVICE_OP_ERROR_COUNT,
                    app_js_dir=g_vars.g_cfg['web']['js_dir'],
                    app_css_dir=g_vars.g_cfg['web']['css_dir'],
                    app_template_dir=g_vars.g_cfg['web']['template_dir'],
                    title="Device Op Error Count",
                    op_log_url=rxg_consts.Node_URLs.APP_DEVICE_OP_LOG[1:])


class AppZbModuleAdm(UIBase):
    def GetTitle(self):
        return "Zigbee Module Adm powered by RoundGIS Lab"

    async def async_get(self):
        self.render(rxg_consts.Node_TPL_NAMES.APP_ADM_ZB_MODULE,
                    app_js_dir=g_vars.g_cfg['web']['js_dir'],
                    app_css_dir=g_vars.g_cfg['web']['css_dir'],
                    app_template_dir=g_vars.g_cfg['web']['template_dir'],
                    title=self.GetTitle(),
                    sync_zb_dev_url=rxg_consts.Node_URLs.APP_SYNC_ZB_DEVICE[1:],
                    restore_module_url=rxg_consts.Node_URLs.APP_RESTORE_ZB_MODULE[1:])


class AppRestoreZbModule(UIBase):
    def GetTitle(self):
        return "Restore Zigbee Module powered by RoundGIS Lab"

    async def async_get(self):
        moduleid = self.get_argument("moduleid")
        self.render(rxg_consts.Node_TPL_NAMES.APP_RESTORE_ZB_MODULE,
                    app_js_dir=g_vars.g_cfg['web']['js_dir'],
                    app_css_dir=g_vars.g_cfg['web']['css_dir'],
                    app_template_dir=g_vars.g_cfg['web']['template_dir'],
                    title=self.GetTitle(),
                    target_moduleid=moduleid)


