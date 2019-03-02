import sys
from twisted.internet import reactor, defer
from twisted.python import log, logfile
import beat_tasks
import web_app
import settings
import api_core
import xy_lib


def InitWebService():
    reactor.listenTCP(settings.HTTP_PORT, web_app.App())


async def Init():
    await api_core.BizDB.Init()
    await api_core.LogDB.Init()
    await xy_lib.Api.ProbeModule()
    InitWebService()
    await beat_tasks.Setup()


def main():
    try:
        log.startLogging(logfile.DailyLogFile.fromFullPath(settings.LOG_PATH + "/" +
                                                           "rxg" +''.join([i for i in settings.HOST if i != '.']) + "_log.txt"),
                         setStdout=False)
        reactor.callLater(1, defer.ensureDeferred, Init())
        reactor.addSystemEventTrigger('before', 'shutdown', beat_tasks.Shutdown)
        reactor.addSystemEventTrigger('before', 'shutdown', api_core.BizDB.Close)
        reactor.addSystemEventTrigger('before', 'shutdown', api_core.LogDB.Close)
        reactor.run()
    except Exception:
        log.err()


if __name__ == "__main__":
    args = sys.argv
    main()

