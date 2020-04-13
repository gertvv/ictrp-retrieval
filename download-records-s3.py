#!/usr/bin/python3
import sys
import gzip
import datetime
import tempfile
import boto3

import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

ch = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('[%(levelname)s] %(asctime)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

import listRecords
import download

def main():
    try:
        dataset = 'ictrp-raw-{}-w{:02d}.xml.gz'.format(*datetime.datetime.today().isocalendar())
        idlist = listRecords.allList()
        with tempfile.TemporaryFile() as tmpfile:
            with gzip.GzipFile('raw.xml.gz', 'w', 9, tmpfile) as outfile:
                failed = download.downloadRecords(idlist, outfile, True)
                logger.info("Failed (all attempts): {}".format(str(failed)))
            tmpfile.seek(0)
            # write to s3
            s3 = boto3.resource('s3')
            object = s3.Bucket('ictrp-data').put_object(Key=dataset, Body=tmpfile)
            object.Acl().put(ACL='public-read')
    except:
        logging.error("ICTRP download failed", exc_info=True)

if __name__ == "__main__":
    main()
