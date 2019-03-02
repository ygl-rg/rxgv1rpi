from twisted.internet import defer
import models
import api_core
import xy_lib
import rg_lib
import rxg_consts


get_val_func_tbl = {
    xy_lib.DeviceNo.XY_SWITCH: xy_lib.Api.GetSwitchStatus,
    xy_lib.DeviceNo.XY_SOIL_3IN1_SENSOR: xy_lib.Api.GetSoil3IN1,
    xy_lib.DeviceNo.XY_LIQUID_LEVEL_SENSOR: xy_lib.Api.GetLiquidLevel,
    xy_lib.DeviceNo.XY_TEMP_HUMIDITY_SENSOR: xy_lib.Api.GetTemperatureHumidity,
    xy_lib.DeviceNo.XY_ILLUMINATION_SENSOR: xy_lib.Api.GetAnalog,
    xy_lib.DeviceNo.XY_CO2_SENSOR: xy_lib.Api.GetAnalog
}


async def Add(device_tbl, ignored=False):
    mdl = models.ZbDevice.BeforeAdd(device_tbl)
    await api_core.BizDB.Interaction([models.ZbDevice.DynInsert(mdl, ignored)])
    return mdl['id']


async def Update(device):
    mdl = models.ZbDevice.BeforeSet(device)
    await api_core.BizDB.Interaction([models.ZbDevice.DynUpdate(mdl)])
    return mdl['id']


def RemoveFromDB(deviceids):
    return api_core.BizDB.Interaction(models.ZbDevice.SqlRows_Remove(deviceids))


async def Get(sql_row):
    rows = await api_core.BizDB.Query(sql_row)
    return rows[0] if rows else None


def Sync(raw_devices):
    sql_rows = []
    for dev in raw_devices:
        sql_rows.append(["""update or ignore rxg_zb_device set nid=?,moduleid=?,device_no=? where id=?""",
                         (dev['nid'], dev['moduleid'], dev['device_no'], dev['mac'])])
        sql_rows.append(models.ZbDevice.DynInsert(models.ZbDevice.SyncDevice(dev), True))
    return api_core.BizDB.Interaction(sql_rows)


def ResetNetwork(deviceids):
    sql_rows = []
    for devid in deviceids:
        sql_rows.append(["update rxg_zb_device set nid=?, moduleid=? where id=?", (-1, '', devid)])
    return api_core.BizDB.Interaction(sql_rows)


def TryUpdateNId(deviceid, nid):
    sql_rows = [["update or ignore rxg_zb_device set nid=? where id=?",(nid, deviceid)]]
    return api_core.BizDB.Interaction(sql_rows)


def Search(para):
    """
    :param para: {"name", "val"}
    :return: [cfg,...]
    """
    if para['name'] == "name":
        sql_str = """select r1.* from rxg_zb_device r1 where r1.name like ? limit ?"""
    elif para['name'] == "id":
        sql_str = """select r1.* from rxg_zb_device r1 where r1.id like ? limit ?"""
    else:
        raise rg_lib.RGError(models.ErrorTypes.UnsupportedOp())
    sql_args = ("{0}%".format(para['val']), rxg_consts.DbConsts.SEARCH_LIMIT)
    return api_core.BizDB.Query([sql_str, sql_args])


async def CheckNId(device):
    if models.ZbDevice.IsValidNId(device):
        sql_str = "select nid from rxg_zb_device where nid=?"
        row = await Get([sql_str, [device['nid']]])
        if row:
            raise rg_lib.RGError(rg_lib.ErrorType.SqliteIntegrityError())
        else:
            return True
    else:
        raise rg_lib.RGError(models.ErrorTypes.InvalidNetworkId())


async def SyncVal(device_mdl):
    if device_mdl:
        device_mdl['vals'] = []
        func = get_val_func_tbl.get(device_mdl['device_no'], None)
        if func:
            try:
                result = await func(device_mdl['nid'], device_mdl['moduleid'])
                if len(result['devices']) > 0:
                    device_mdl['vals'] = result['devices'][0]['vals']
                else:
                    await api_core.DeviceLog.Add(models.DeviceOpLog.make(rg_lib.DateTime.ts(),
                                                                         device_mdl['id'],
                                                                         result['req'], result['res']))
            except xy_lib.NoModuleError:
                pass
    return device_mdl


async def SetSwitchStatus(device_mdl, turn_on):
    if device_mdl:
        device_mdl['vals'] = []
        try:
            result = await xy_lib.Api.SetSwitchStatus(device_mdl['nid'], turn_on, device_mdl['moduleid'])
            if len(result['devices']) > 0:
                device_mdl['vals'] = result['devices'][0]['vals']
            else:
                await api_core.DeviceLog.Add(models.DeviceOpLog.make(rg_lib.DateTime.ts(),
                                                                     device_mdl['id'],
                                                                     result['req'], result['res']))
        except xy_lib.NoModuleError:
            pass
    return device_mdl


async def OpSwitch(deviceid, on_off):
    dev = await Get(["select * from rxg_zb_device where id=?",
                     (deviceid,)])
    await SetSwitchStatus(dev, on_off)
    return dev


async def __Reset(deviceids):
    sql_str = rg_lib.Sqlite.GenInSql("select id, nid, moduleid from rxg_zb_device where id in ", deviceids)
    sql_str += " and nid > 0"
    devs = await api_core.BizDB.Query([sql_str, deviceids])
    for dev in devs:
        try:
            await xy_lib.Api.RemoveDevice(dev['nid'], dev['id'], dev['moduleid'])
        except xy_lib.NoModuleError:
            pass


async def Reboot(deviceids):
    sql_str = rg_lib.Sqlite.GenInSql("select id, nid, moduleid from rxg_zb_device where id in ", deviceids)
    sql_str += " and nid > 0"
    devs = await api_core.BizDB.Query([sql_str, deviceids])
    for dev in devs:
        try:
            await xy_lib.Api.RebootDevice(dev['nid'], dev['moduleid'])
        except xy_lib.NoModuleError:
            pass


async def Remove(deviceids):
    await __Reset(deviceids)
    await RemoveFromDB(deviceids)


async def Reset(deviceids):
    await __Reset(deviceids)
    await ResetNetwork(deviceids)


async def GetVal(deviceids):
    sql_str = rg_lib.Sqlite.GenInSql("""select id, nid, name, moduleid,device_no 
                                        from rxg_zb_device where nid > 0 and id in """,
                                     deviceids)
    sql_args = deviceids
    devs = await api_core.BizDB.Query([sql_str, sql_args])
    for dev in devs:
        await SyncVal(dev)
    return devs


async def List(list_no, get_vals):
    """
    :param list_no: switch or sensor
    :param get_vals: boolean
    :return: devices
    """
    if list_no == 'switch':
        sql_str = "select id, nid, moduleid, name, device_no from rxg_zb_device where device_no=?"
        sql_args = [xy_lib.DeviceNo.XY_SWITCH]
    elif list_no == 'sensor':
        sql_str = """select r1.id id, 
                            r1.nid nid,
                            r1.moduleid moduleid,
                            r1.name name,  
                            r1.device_no device_no
                     from rxg_zb_device r1 where r1.device_no <> ?"""
        sql_args = [xy_lib.DeviceNo.XY_SWITCH]
    elif list_no == 'all':
        sql_str = """select r1.id id, 
                            r1.nid nid,
                            r1.moduleid moduleid,
                            r1.name name, 
                            r1.device_no device_no
                     from rxg_zb_device r1"""
        sql_args = []
    else:
        raise rg_lib.RGError(models.ErrorTypes.UnsupportedOp())
    devices = await api_core.BizDB.Query([sql_str, sql_args])
    if get_vals:
        for dev in devices:
            await SyncVal(dev)
    return devices


class Module:
    @classmethod
    async def Query(cls, sql_row):
        rows = await api_core.BizDB.Query(sql_row)
        return [models.ZbModule.FromRow(row) for row in rows]

    @classmethod
    def Upsert(cls, zb_module):
        sql_rows = [
            models.ZbModule.DynInsert(zb_module, True),
            models.ZbModule.DynUpdate(zb_module, True)
        ]
        return api_core.BizDB.Interaction(sql_rows)

    @classmethod
    async def List(cls, arg):
        """
        :param arg: {list_no: "active", "backup"}
        :return:
        """
        if arg['list_no'] == 'active':
            return xy_lib.Api.GetModules()
        elif arg['list_no'] == 'backup':
            sql_str = "select id, serial_port_name, baud_rate from rxg_zb_module"
            mods = await cls.Query([sql_str, []])
            return mods
        else:
            raise rg_lib.RGError(models.ErrorTypes.UnsupportedOp())

    @classmethod
    async def ProbeDevice(cls, moduleid):
        """
        :param moduleid: {moduleid: }
        :return: {"devices": []}
        """
        devs = await xy_lib.Api.ProbeDevice(moduleid)
        if len(devs) > 0:
            devs_tbl = {i['mac']: i for i in devs}
            for k in devs_tbl:
                devs_tbl[k]['moduleid'] = moduleid
            devs = [devs_tbl[k] for k in devs_tbl]
            await Sync(devs)
        return {'devices': devs}

    @classmethod
    async def Backup(cls, moduleid):
        module_tbl = xy_lib.Api.GetModule(moduleid)
        module_tbl['backup_data'] = await xy_lib.Api.BackupModule(moduleid)
        await cls.Upsert(models.ZbModule.Filter(module_tbl))

    @classmethod
    async def Restore(cls, target_moduleid, src_moduleid):
        sql_str = "select * from rxg_zb_module where id=?"
        rows = await cls.Query([sql_str, (src_moduleid,)])
        row = rows[0] if len(rows) > 0 else None
        flag = False
        if row and models.ZbModule.HasBackupData(row):
            flag = await xy_lib.Api.RestoreModule(target_moduleid, row['backup_data'])
        return flag
