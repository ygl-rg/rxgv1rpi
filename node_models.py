# -*- coding: utf-8 -*-
import json
import rg_lib


class ErrorTypes:
    @classmethod
    def UnsupportedOp(cls):
        return rg_lib.ErrorType.DeclaredType("UnsupportedOp")

    @classmethod
    def InvalidNetworkId(cls):
        return rg_lib.ErrorType.DeclaredType("InvalidNetworkId")


class MultiText:
    @classmethod
    def GetValue(cls, text, lang='en'):
        if lang != 'en':
            if lang in text:
                return text[lang]
            else:
                return text.get('en')
        else:
            return text.get('en')


class ZbDevice:
    TBL = 'rxg_zb_device'

    TBL_FIELDS = [
        {'name': 'id', 'type': 'varchar(64) primary key'},
        {'name': 'nid', 'type': 'integer not null default -1'},
        {'name': 'moduleid', 'type': "varchar(64) not null default ''"},
        {'name': 'name', 'type': 'varchar(64) not null'},
        {'name': 'cts', 'type': 'datetime not null'},
        {'name': 'device_no', 'type': 'varchar(64) not null'},
        {'name': 'remark', 'type': 'text'},
        {'name': 'vals', 'type': "text not null default '[]'"}
    ]

    IDX1 = """
    create index if not exists rxg_zb_device_idx1 on rxg_zb_device(nid)
    """

    IDX2 = """
    create index if not exists rxg_zb_device_idx2 on rxg_zb_device(moduleid)
    """

    @classmethod
    def Init(cls, conn_obj):
        conn_obj.execute(rg_lib.Sqlite.CreateTable(cls.TBL, cls.TBL_FIELDS))
        conn_obj.execute(cls.IDX1)
        conn_obj.execute(cls.IDX2)

    @classmethod
    def SqlRows_Remove(cls, deviceids):
        sqls = []
        if isinstance(deviceids, list):
            for devid in deviceids:
                sqls.append(["delete from rxg_zb_device where id=?", (devid,)])
        else:
            sqls.append(["delete from rxg_zb_device where id=?", (deviceids,)])
        return sqls

    @classmethod
    def SyncDevice(cls, device):
        temp = {'device_no': device['device_no'],
                'id': device['mac'], 'nid': device['nid'],
                'moduleid': device['moduleid'],
                'name': 'sync from coordinator'}
        return cls.BeforeAdd(temp)

    @classmethod
    def BeforeAdd(cls, device):
        device['cts'] = rg_lib.DateTime.ts()
        return rg_lib.Dict.DelKeys(device, 'vals')

    @classmethod
    def BeforeSet(cls, device):
        return rg_lib.Dict.DelKeys(device, 'nid', 'cts', 'vals')

    @classmethod
    def DynUpdate(cls, mdl):
        """
        :param mdl: zigbee device model
        :return: [sql, sql_args]
        """
        terms = []
        args = []
        for key in mdl:
            if key not in ('id',):
                terms.append("{0}=?".format(key))
                args.append(mdl[key])
        update_sql = "update rxg_zb_device set "
        update_sql += ",".join(terms)
        update_sql += " where id=?"
        args.append(mdl['id'])
        return [update_sql, args]

    @classmethod
    def DynInsert(cls, rec_tbl, ignored=False):
        terms = []
        args = []
        marks = []
        for key in rec_tbl:
            terms.append(key)
            marks.append("?")
            args.append(rec_tbl[key])
        if ignored:
            insert_sql = "insert or ignore into rxg_zb_device("
        else:
            insert_sql = "insert into rxg_zb_device("
        insert_sql += ",".join(terms)
        insert_sql += ") values ("
        insert_sql += ",".join(marks)
        insert_sql += ")"
        return [insert_sql, args]

    @classmethod
    def HasVals(cls, mdl):
        return (mdl is not None) and isinstance(mdl.get('vals', None), list)

    @classmethod
    def ValsNotEmpty(cls, mdl):
        return cls.HasVals(mdl) and len(mdl['vals']) > 0

    @classmethod
    def IsValidNId(cls, mdl):
        return isinstance(mdl.get('nid', None), int) and mdl['nid'] > 0


class ZbModule:
    TBL = 'rxg_zb_module'

    TBL_FIELDS = [
        {'name': 'id', 'type': 'varchar(64) primary key'},
        {'name': 'baud_rate', 'type': 'integer not null default 38400'},
        {'name': 'serial_port_name', 'type': 'text not null'},
        {'name': 'backup_data', 'type': "text not null default '{}'"},
        {'name': 'uts', 'type': "datetime not null default 0"}
    ]

    @classmethod
    def Init(cls, conn_obj):
        conn_obj.execute(rg_lib.Sqlite.CreateTable(cls.TBL, cls.TBL_FIELDS))

    @classmethod
    def SqlRows_Remove(cls, ids):
        sqls = []
        for devid in ids:
            sqls.append(["delete from rxg_zb_module where id=?", (devid,)])
        return sqls

    @classmethod
    def Filter(cls, device):
        return rg_lib.Dict.DelKeys(device, 'has_backup_data')

    @classmethod
    def DynUpdate(cls, mdl, ignored=False):
        """
        :param mdl: zigbee module model
        :return: [sql, sql_args]
        """
        terms = []
        args = []
        for key in mdl:
            if key not in ('id', 'backup_data'):
                terms.append("{0}=?".format(key))
                args.append(mdl[key])
        if cls.HasBackupData(mdl):
            terms.append("backup_data=?")
            args.append(json.dumps(mdl['backup_data']))
        if ignored:
            update_sql = "update or ignore rxg_zb_module set "
        else:
            update_sql = "update rxg_zb_module set "
        update_sql += ",".join(terms)
        update_sql += " where id=?"
        args.append(mdl['id'])
        return [update_sql, args]

    @classmethod
    def DynInsert(cls, mdl, ignored=False):
        terms = []
        args = []
        marks = []
        for key in mdl:
            if key not in ('backup_data',):
                terms.append(key)
                marks.append("?")
                args.append(mdl[key])
        if cls.HasBackupData(mdl):
            terms.append("backup_data")
            marks.append("?")
            args.append(json.dumps(mdl['backup_data']))
        if ignored:
            insert_sql = "insert or ignore into rxg_zb_module("
        else:
            insert_sql = "insert into rxg_zb_module("
        insert_sql += ",".join(terms)
        insert_sql += ") values ("
        insert_sql += ",".join(marks)
        insert_sql += ")"
        return [insert_sql, args]

    @classmethod
    def FromRow(cls, row_obj):
        if row_obj:
            if 'backup_data' in row_obj:
                row_obj['backup_data'] = json.loads(row_obj['backup_data'])
        return row_obj

    @classmethod
    def HasBackupData(cls, mdl):
        return isinstance(mdl.get('backup_data', None), dict) and (len(mdl['backup_data']) == 2)


class DeviceOpLog:
    TBL = "rxg_device_op_log"
    TBL_FIELDS = [
        {'name': 'deviceid', 'type': 'varchar(64) not null'},
        {'name': 'cts', 'type': 'datetime not null'},
        {'name': 'req', 'type': 'text not null'},
        {'name': 'res', 'type': 'text not null'}]

    FIELDS = ['cts', 'deviceid', 'req', 'res']

    IDX1 = """create index if not exists rxg_device_op_log_idx1 on rxg_device_op_log(cts)"""

    @classmethod
    def Init(cls, conn_obj):
        conn_obj.execute(rg_lib.Sqlite.CreateTable(cls.TBL, cls.TBL_FIELDS,
                                                   'PRIMARY key(deviceid, cts)'))
        conn_obj.execute(cls.IDX1)

    @classmethod
    def make(cls, cts, deviceid, req, res):
        return {'cts': cts, 'deviceid': deviceid, 'req': req, 'res': res}

    @classmethod
    def DynInsert(cls, rec_tbl, ignored=False):
        terms = []
        args = []
        marks = []
        for key in rec_tbl:
            terms.append(key)
            marks.append("?")
            args.append(rec_tbl[key])
        if ignored:
            insert_sql = "insert or ignore into rxg_device_op_log("
        else:
            insert_sql = "insert into rxg_device_op_log("
        insert_sql += ",".join(terms)
        insert_sql += ") values ("
        insert_sql += ",".join(marks)
        insert_sql += ")"
        return [insert_sql, args]
