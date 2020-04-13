#!/usr/bin/python3
import sys

import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

ch = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('[%(levelname)s] %(asctime)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

import listRecords

with open('list.txt', 'w') as outfile:
    for id in listRecords.allList():
        outfile.write(id + '\n') 
