#!/usr/bin/python
import pp
import subprocess
import StringIO
import download
import threading
import time

import logging
import tcplogger

logger = tcplogger.makeLogger(None)
ppLogger = logging.getLogger('pp').setLevel('WARNING')

def main():
    # start logserver
    subprocess.Popen(['./logserver.py'])
    time.sleep(1)

    idlist = []
    outfile = StringIO.StringIO()
    with open('idlist.txt', 'r') as idfile:
        idlist = idfile.read().splitlines()
    job_server = pp.Server(4)
    logger.info('======= START =======')
    print logger.handlers
    jobs = [(id, job_server.submit(download.downloadParallel, (id,), modules=('download','tcplogger', 'traceback'))) for id in idlist]
    failed = [id for (id, job) in jobs if job() == None]
    logger.info('Failed: {}'.format(failed))
    logger.info('======== END ========')
    logger.info('======= START =======')
    failed = [id for id in idlist if not download.processId(outfile, id)]
    logger.info('Failed: {}'.format(failed))
    logger.info('======== END ========')

if __name__ == '__main__':
    main()
