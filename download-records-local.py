#!/usr/bin/python
import sys
import os
import urllib2
import re

import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

ch = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('[%(levelname)s] %(asctime)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

import download

def main():
    with open('idlist.txt', 'r') as idfile, open('raw.xml', 'w') as outfile:
        idlist = idfile.read().splitlines()
        failed = download.downloadRecords(idlist, outfile)
        logger.info("Failed (all attempts): {}".format(str(failed)))

if __name__ == "__main__":
    main()
