import os
import urllib.request, urllib.error, urllib.parse
import shutil
import tempfile
import zipfile
import re

import logging
logger = logging.getLogger()

import xml.etree.cElementTree as ET

from util import stripInvalidXmlEntities

def nctList():
    logger.info("Getting NCT ID list")
    url = 'https://clinicaltrials.gov/ct2/results/download?flds=k&down_stds=all&down_typ=fields&down_flds=shown&down_fmt=xml&show_down=Y'
    request = urllib.request.urlopen(url)
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
    ids = [e.text for e in root.findall('.//nct_id')]
    logger.info('NCT IDs listed: {} IDs found'.format(len(ids)))
    return ids

def ictrpList():
    logger.info("Getting ICTRP ID list")
    url = 'http://apps.who.int/trialsearch/TrialService.asmx/GetTrials?Title=&username={username}&password={password}'.format(username=os.environ['ICTRP_LIST_USERNAME'], password=os.environ['ICTRP_LIST_PASSWORD'])
    logger.info(url)
    request = urllib.request.urlopen(url)
    logger.info('Request complete')
    xml = request.read()
    request.close()
    logger.info('Captured XML string')
    root = ET.fromstring(stripInvalidXmlEntities(xml))
    logger.info('Parsed XML')
    ids = [e.text for e in root.findall('.//TrialID')]
    logger.info('ICTRP IDs listed: {} IDs found'.format(len(ids)))
    return ids

def crawlList():
    baseUrl = "http://apps.who.int/trialsearch/crawl/"

    authinfo = urllib.request.HTTPPasswordMgrWithDefaultRealm()
    authinfo.add_password(None, baseUrl, os.environ['ICTRP_CRAWL_USERNAME'], os.environ['ICTRP_CRAWL_PASSWORD'])
    handler = urllib.request.HTTPBasicAuthHandler(authinfo)
    opener = urllib.request.build_opener(handler)
    urllib.request.install_opener(opener)

    def crawl(page):
        response = urllib.request.urlopen(baseUrl + page)
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

def allList():
    il = frozenset(ictrpList())
    nl = frozenset(nctList())
    cl = frozenset(crawlList())
    al = sorted(cl.union(il, nl))
    logging.info("From Crawl but not listing: {}".format(sorted(cl.difference(il, nl))))
    logging.info("From list but not Crawl: {}".format(sorted(il.difference(cl))))
    logging.info("From ClinicalTrials.gov but not Crawl: {}".format(sorted(nl.difference(cl))))
    return al
