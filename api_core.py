from twisted.python import log
import txredisapi
import rg_lib
import models


class BizDB:
    db_pool = None
    redis_conn = None

    @classmethod
    async def Query(cls, sql_row):
        """
        :param sql_row: [sql, args]
        :return: rows
        """
        return await rg_lib.Sqlite.RunQuery(cls.db_pool, [sql_row])

    @classmethod
    def Interaction(cls, sql_rows):
        return rg_lib.Sqlite.RunInteraction(cls.db_pool, sql_rows)

    @classmethod
    def Init(cls, cfg):
        def helper(conn_obj):
            conn_obj.execute("BEGIN")
            models.ZbModule.Init(conn_obj)
            models.ZbDevice.Init(conn_obj)
        cls.db_pool = rg_lib.Sqlite.MakeConnPool(cfg['db']['biz']['db_path'])
        cls.redis_conn = txredisapi.lazyConnectionPool(host=cfg['redis']['host'],
                                                       port=cfg['redis']['port'],
                                                       charset=None,
                                                       convertNumbers=False)
        return cls.db_pool.runWithConnection(helper)

    @classmethod
    def Close(cls):
        if cls.db_pool:
            cls.db_pool.close()
            cls.db_pool = None
        if cls.redis_conn:
            cls.redis_conn.quit()
            cls.redis_conn = None


class LogDB:
    db_pool = None

    @classmethod
    def Interaction(cls, sql_rows):
        return rg_lib.Sqlite.RunInteraction(cls.db_pool, sql_rows)

    @classmethod
    async def Query(cls, sql_row):
        """
        :param sql_row: [sql, args]
        :return: SensorData objs
        """
        return await rg_lib.Sqlite.RunQuery(cls.db_pool, [sql_row])

    @classmethod
    def Init(cls, cfg):
        def helper(conn_obj):
            conn_obj.execute("BEGIN")
            models.DeviceOpLog.Init(conn_obj)

        cls.db_pool = rg_lib.Sqlite.MakeConnPool(cfg['db']['log']['db_path'])
        return cls.db_pool.runWithConnection(helper)

    @classmethod
    def Close(cls):
        if cls.db_pool:
            cls.db_pool.close()
            cls.db_pool = None


class DeviceLog:
    @classmethod
    async def Add(cls, op_logs):
        if not isinstance(op_logs, list):
            op_logs = [op_logs]
        sql_rows = [models.DeviceOpLog.DynInsert(i, True) for i in op_logs]
        return await LogDB.Interaction(sql_rows)

    @classmethod
    def Get(cls, start_ts, stop_ts, deviceid, count=10000):
        sql_str = """select * from rxg_device_op_log r1 
                      where r1.deviceid =? and cts>=? and cts<? limit {0}""".format(count)
        sql_args = [deviceid, rg_lib.DateTime.dt2ts(start_ts), rg_lib.DateTime.dt2ts(stop_ts)]
        return LogDB.Query([sql_str, sql_args])

    @classmethod
    def GetErrorCount(cls, start_ts, stop_ts, deviceids):
        sql_str = rg_lib.Sqlite.GenInSql("""select deviceid, count(1) error_count 
                                            from rxg_device_op_log where deviceid in """,
                                         deviceids)
        sql_str += " and cts>=? and cts<? group by deviceid"
        sql_args = deviceids + [rg_lib.DateTime.dt2ts(start_ts), rg_lib.DateTime.dt2ts(stop_ts)]
        return LogDB.Query([sql_str, sql_args])

    @classmethod
    def RemoveTTL(cls, ts_val):
        return LogDB.Interaction([
            ["delete from rxg_device_op_log where cts < ?", (ts_val,)]
        ])




