import os
import urllib2
import shutil
import tempfile
import zipfile
import re

import logging
logger = logging.getLogger()

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
    logger.info('NCT IDs listed: {} IDs found'.format(len(ids)))
    return ids

def ictrpList():
    logger.info("Getting ICTRP ID list")
    url = 'http://apps.who.int/trialsearch/TrialService.asmx/GetTrials?Title=&username={username}&password={password}'.format(username=os.environ['ICTRP_LIST_USERNAME'], password=os.environ['ICTRP_LIST_PASSWORD'])
    logger.info(url)
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
    logger.info('ICTRP IDs listed: {} IDs found'.format(len(ids)))
    return ids

def crawlList():
    baseUrl = "http://apps.who.int/trialsearch/crawl/"

    authinfo = urllib2.HTTPPasswordMgrWithDefaultRealm()
    authinfo.add_password(None, baseUrl, os.environ['ICTRP_CRAWL_USERNAME'], os.environ['ICTRP_CRAWL_PASSWORD'])
    handler = urllib2.HTTPBasicAuthHandler(authinfo)
    opener = urllib2.build_opener(handler)
    urllib2.install_opener(opener)

    def crawl(page):
        response = urllib2.urlopen(baseUrl + page)
        body = response.read()
        response.close()
        return body

    pages = re.findall('href\="(crawl[0-9]+.aspx)"', crawl("crawl0.aspx"))
    logging.info("Crawl - got index, {} pages".format(len(pages)))
    ids = []
    for page in pages:
        data = re.findall('trialid\=([A-Za-z0-9\-\/]+)', crawl(page))
        logging.info("Crawl - got {}, {} IDs".format(page, len(data)))
        ids.extend(data)
    return ids
