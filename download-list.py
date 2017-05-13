#!/usr/bin/python
import sys
import os
import urllib2
import shutil
import tempfile
import zipfile

import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

ch = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('[%(levelname)s] %(asctime)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

import xml.etree.cElementTree as ET

def nctList():
    logger.info("Getting NCT ID list")
    url = 'https://clinicaltrials.gov/ct2/results/download?flds=k&down_stds=all&down_typ=fields&down_flds=shown&down_fmt=xml&show_down=Y'
    request = urllib2.urlopen(url)
    logger.info('Request complete')
    tmpfile = tempfile.TemporaryFile()
    shutil.copyfileobj(request, tmpfile)
    request.close()
    logger.info('Copied to temporary file')
    z = zipfile.ZipFile(tmpfile, 'r')
    xml = z.open('study_fields.xml', 'r')
    logger.info('Opened ZIP contents')
    root = ET.parse(xml)
    logger.info('Parsed XML')
    xml.close()
    z.close()
    tmpfile.close()
    ids = map(lambda e: e.text, root.findall('.//nct_id'))
    logger.info('NCT IDs listed')
    return ids

def ictrpList():
    logger.info("Getting ICTRP ID list")
    url = 'http://apps.who.int/trialsearch/TrialService.asmx/GetTrials?Title=&username={username}&password={password}'.format(password=os.environ['ICTRP_LIST_USERNAME'], username=os.environ['ICTRP_LIST_PASSWORD'])
    request = urllib2.urlopen(url)
    logger.info('Request complete')
    tmpfile = tempfile.TemporaryFile()
    shutil.copyfileobj(request, tmpfile)
    request.close()
    logger.info('Copied to temporary file')
    tmpfile.seek(0)
    root = ET.parse(tmpfile)
    logger.info('Parsed XML')
    tmpfile.close()
    ids = map(lambda e: e.text, root.findall('.//TrialID'))
    logger.info('ICTRP IDs listed')
    return ids

with open('list.txt', 'w') as outfile:
    for id in ictrpList():
        outfile.write(id + '\n') 
    for id in nctList():
        outfile.write(id + '\n') 
