import functools
from twisted.python import log
import rg_lib
import api_core
import api_device
import xy_lib


class EM:
    @classmethod
    async def ListDevice(cls, req_handler, arg):
        """
        :param req_handler: http request
        :param arg: {token, list_no: switch or sensor or all,
                     get_vals, optional}
        :return: devices
        """
        try:
            return await api_device.List(arg['list_no'], arg.get('get_vals', False))
        except Exception:
            rg_lib.Cyclone.HandleErrInException()

    @classmethod
    async def OpenSwitch(cls, req_handler, para):
        """
        :param sessionid:
        :param para: {"token", "arg": {"deviceid"}}
        :return:
        """
        try:
            return await api_device.OpSwitch(para['arg']['deviceid'], True)
        except Exception:
            rg_lib.Cyclone.HandleErrInException()

    @classmethod
    async def OpenMultiSwitch(cls, req_handler, para):
        """
        :param sessionid:
        :param para: {"token", "arg": {"deviceids"}}
        :return: devices
        """
        try:
            devs = []
            for devid in para['arg']['deviceids']:
                devs.append(await api_device.OpSwitch(devid, True))
            return devs
        except Exception:
            rg_lib.Cyclone.HandleErrInException()

    @classmethod
    async def CloseSwitch(cls, req_handler, para):
        """
        :param sessionid:
        :param para: {"arg": {"deviceid"}}
        :return:
        """
        try:
            return await api_device.OpSwitch(para['arg']['deviceid'], False)
        except Exception:
            rg_lib.Cyclone.HandleErrInException()

    @classmethod
    async def CloseMultiSwitch(cls, req_handler, para):
        """
        :param sessionid:
        :param para: {"token", "arg": {"deviceids"}}
        :return:
        """
        try:
            devs = []
            for devid in para['arg']['deviceids']:
                devs.append(await api_device.OpSwitch(devid, False))
            return devs
        except Exception:
            rg_lib.Cyclone.HandleErrInException()

    @classmethod
    async def ReadDevice(cls, req_handler, para):
        try:
            return await api_device.GetVal(para['deviceids'])
        except Exception:
            rg_lib.Cyclone.HandleErrInException()


class ZbDevice:
    @classmethod
    async def __GetDevice(cls, deviceid):
        return await api_device.Get(["""select r1.* 
                                        from rxg_zb_device r1 
                                        where r1.id=?""", (deviceid,)])

    @classmethod
    async def Remove(cls, req_handler, arg):
        """
        :param req_handler:
        :param limit_key:
        :param arg: {token, deviceids}
        :return:
        """
        try:
            await api_device.Remove(arg['deviceids'])
            return "ok"
        except Exception:
            rg_lib.Cyclone.HandleErrInException()

    @classmethod
    async def Reset(cls, req_handler, arg):
        """
        :param req_handler:
        :param limit_key:
        :param arg: {token, deviceids}
        :return:
        """
        try:
            await api_device.Reset(arg['deviceids'])
            return "ok"
        except Exception:
            rg_lib.Cyclone.HandleErrInException()

    @classmethod
    async def Add(cls, req_handler, arg):
        """
        :param req_handler:
        :param limit_key:
        :param arg: {token, device}
        :return:
        """
        try:
            await api_device.CheckNId(arg['device'])
            return await cls.__GetDevice(await api_device.Add(arg['device']))
        except Exception:
            rg_lib.Cyclone.HandleErrInException()

    @classmethod
    async def Set(cls, req_handler, arg):
        """
        :param req_handler:
        :param limit_key:
        :param arg: {token, device}
        :return:
        """
        try:
            return await cls.__GetDevice(await api_device.Update(arg['device']))
        except Exception:
            rg_lib.Cyclone.HandleErrInException()

    @classmethod
    async def Get(cls, req_handler, arg):
        try:
            return await cls.__GetDevice(arg['deviceid'])
        except Exception:
            rg_lib.Cyclone.HandleErrInException()

    @classmethod
    async def Search(cls, req_handler, para):
        """
        :param req_handler:
        :param sessionid:
        :param para: {"name": xxx, "val": xxx}
        :return:
        """
        try:
            return await api_device.Search(para)
        except Exception:
            rg_lib.Cyclone.HandleErrInException()

    @classmethod
    async def GetOpLog(cls, req_handler, arg):
        """
        :param req_handler:
        :param arg: {"deviceid": deviceid, "start_ts": start timestamp, "stop_ts": stop timestamp}
        :return:
        """
        try:
            return await api_core.DeviceLog.Get(arg['start_ts'], arg['stop_ts'], arg['deviceid'])
        except Exception:
            rg_lib.Cyclone.HandleErrInException()

    @classmethod
    async def GetOpErrorCount(cls, req_handler, arg):
        """
        :param req_handler:
        :param arg: {token, start_ts, stop_ts}
        :return:
        """
        try:
            devs = await api_core.BizDB.Query(["select id, name, device_no from rxg_zb_device", []])
            devids = [i['id'] for i in devs]
            devs_tbl = {i['id']: i for i in devs}
            recs = await api_core.DeviceLog.GetErrorCount(arg['start_ts'], arg['stop_ts'], devids)
            for rec in recs:
                rec['device_no'] = devs_tbl[rec['deviceid']]['device_no']
                rec['device_name'] = devs_tbl[rec['deviceid']]['name']
            return recs
        except Exception:
            rg_lib.Cyclone.HandleErrInException()

    @classmethod
    async def GetNId(cls, req_handler, arg):
        """
        :param req_handler:
        :param arg: {token, deviceid, moduleid}
        :return:
        """
        try:
            res = {"nid": -1, "count": 0}
            for i in range(10):
                res['count'] = i + 1
                await rg_lib.Twisted.sleep(1)
                nid = await xy_lib.Api.GetDeviceNId(arg['deviceid'], arg['moduleid'])
                if nid is not None:
                    res['nid'] = nid
                    break
            if res['nid'] > 0:
                await api_device.TryUpdateNId(arg['deviceid'], res['nid'])
            return res
        except Exception as e:
            rg_lib.Cyclone.HandleErrInException()

    @classmethod
    async def Reboot(cls, req_handler, arg):
        try:
            await api_device.Reboot(arg['deviceids'])
            return "ok"
        except Exception:
            rg_lib.Cyclone.HandleErrInException()


class ZbModule:
    @classmethod
    async def List(cls, req_handler, arg):
        """
        :param req_handler:
        :param arg: {list_no: "active", "backup"}
        :return:
        """
        try:
            return await api_device.Module.List(arg)
        except Exception as e:
            rg_lib.Cyclone.HandleErrInException()

    @classmethod
    async def ProbeDevice(cls, req_handler, para):
        """
        :param req_handler:
        :param para: {token, moduleid: }
        :return: {"devices": []}
        """
        try:
            return await api_device.Module.ProbeDevice(para['moduleid'])
        except Exception as e:
            rg_lib.Cyclone.HandleErrInException()

    @classmethod
    async def Reboot(cls, req_handler, arg):
        try:
            await xy_lib.Api.RebootModule(arg['moduleid'])
            return 'ok'
        except Exception as e:
            rg_lib.Cyclone.HandleErrInException()

    @classmethod
    async def Reset(cls, req_handler, arg):
        try:
            await xy_lib.Api.ClearModule(arg['moduleid'])
            await xy_lib.Api.RebootModule(arg['moduleid'])
            return 'ok'
        except Exception as e:
            rg_lib.Cyclone.HandleErrInException()

    @classmethod
    async def Backup(cls, req_handler, arg):
        try:
            await api_device.Module.Backup(arg['moduleid'])
            return 'ok'
        except Exception as e:
            rg_lib.Cyclone.HandleErrInException()

    @classmethod
    async def Restore(cls, req_handler, arg):
        try:
            flag = await api_device.Module.Restore(arg['target_moduleid'], arg['src_moduleid'])
            return 'ok' if flag else 'failed'
        except Exception as e:
            rg_lib.Cyclone.HandleErrInException()

    @classmethod
    async def RebootAll(cls, req_handler, arg):
        try:
            await xy_lib.Api.RebootAll()
            return 'ok'
        except Exception as e:
            rg_lib.Cyclone.HandleErrInException()


class _SysCfg:
    @classmethod
    async def RebootSys(cls, req_handler):
        from twisted.internet import reactor
        try:
            tp = rg_lib.ProcessProto('reboot')
            reactor.spawnProcess(tp, '/sbin/reboot', ['/sbin/reboot'], {})
            return 'ok'
        except Exception:
            rg_lib.Cyclone.HandleErrInException()

    @classmethod
    async def RestartRXG(cls, req_handler):
        import os
        try:
            rg_lib.Process.Kill(os.getpid())
            return 'ok'
        except Exception:
            rg_lib.Cyclone.HandleErrInException()


class Base(rg_lib.AsyncDynFuncHandler):
    def initialize(self, **kwargs):
        self.FUNC_TBL = {}

    def GetFunc(self, func_name):
        return self.FUNC_TBL[func_name] if func_name in self.FUNC_TBL else None


class EnvMonitor(Base):
    def initialize(self, **kwargs):
        self.FUNC_TBL = {'ListDevice': functools.partial(EM.ListDevice, self),
                         'OpenSwitch': functools.partial(EM.OpenSwitch, self),
                         'OpenMultiSwitch': functools.partial(EM.OpenMultiSwitch, self),
                         'CloseSwitch': functools.partial(EM.CloseSwitch, self),
                         'CloseMultiSwitch': functools.partial(EM.CloseMultiSwitch, self),
                         'ReadDevice': functools.partial(EM.ReadDevice, self)}


class ZbDeviceAdm(Base):
    def initialize(self, **kwargs):
        self.FUNC_TBL = {"AddDevice": functools.partial(ZbDevice.Add, self),
                         "SetDevice": functools.partial(ZbDevice.Set, self),
                         "GetDevice": functools.partial(ZbDevice.Get, self),
                         "GetDeviceNId": functools.partial(ZbDevice.GetNId, self),
                         'RemoveDevice': functools.partial(ZbDevice.Remove, self),
                         'ResetDevice': functools.partial(ZbDevice.Reset, self),
                         'SearchDevice': functools.partial(ZbDevice.Search, self),
                         'GetDeviceOpLog': functools.partial(ZbDevice.GetOpLog, self),
                         'GetDeviceOpErrorCount': functools.partial(ZbDevice.GetOpErrorCount, self),
                         'RebootDevice': functools.partial(ZbDevice.Reboot, self)
                         }


class ZbModuleAdm(Base):
    def initialize(self, **kwargs):
        self.FUNC_TBL = {"ListModule": functools.partial(ZbModule.List, self, "3_1"),
                         'ProbeDevice': functools.partial(ZbModule.ProbeDevice, self, "3_2"),
                         'ResetModule': functools.partial(ZbModule.Reset, self, "3_3"),
                         'BackupModule': functools.partial(ZbModule.Backup, self, "3_4"),
                         'RestoreModule': functools.partial(ZbModule.Restore, self, "3_5"),
                         'RebootModule': functools.partial(ZbModule.Reboot, self, "3_6"),
                         'RebootAll': functools.partial(ZbModule.RebootAll, self, "3_7")}


class SysCfg(Base):
    def initialize(self, **kwargs):
        self.FUNC_TBL = {"RebootSys": functools.partial(_SysCfg.RebootSys, self),
                         "RestartRXG": functools.partial(_SysCfg.RestartRXG, self)}

