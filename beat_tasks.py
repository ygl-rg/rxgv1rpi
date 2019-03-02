from twisted.internet import defer, task
from twisted.python import log
import rg_lib
import api_core
import settings


jobs_tbl = {}


async def RemoveTTL():
    try:
        await api_core.DeviceLog.RemoveTTL(rg_lib.DateTime.ts() - int(settings.LOG_DB['ttl'] * 2))
    except Exception:
        log.err()


async def Setup():
    await SetupRemoveTTL()


def SetupRemoveTTL():
    __StopTask('remove_ttl')
    jobs_tbl['remove_ttl'] = task.LoopingCall(lambda: defer.ensureDeferred(RemoveTTL()))
    return jobs_tbl['remove_ttl'].start(60*10, False)


def __StopTask(taskid):
    if taskid in jobs_tbl:
        jobs_tbl[taskid].stop()
        del jobs_tbl[taskid]


def Shutdown():
    __StopTask('remove_ttl')


