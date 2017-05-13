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

import xml.etree.cElementTree as ET
ET.register_namespace("diffgr", "urn:schemas-microsoft-com:xml-diffgram-v1")

urlTemplate = "http://apps.who.int/trialsearch/TrialService.asmx/GetTrialDetails?TrialIDnum={id}&username={username}&password={password}"

def download(id):
    url = urlTemplate.format(id=id,
        username=os.environ['ICTRP_GET_USERNAME'],
        password=os.environ['ICTRP_GET_PASSWORD'])
    request = urllib2.urlopen(url, timeout=60)
    response = request.read()
    request.close()
    return response

def reduceXml(xml):
    # ChiCTR records may (very rarely) contain invalid XML entities
    # The following were seen: &#x2;, &#x8;, &#x1F;
    xml = re.sub("&#x([0-8BCEF]|1[0-9A-F]);", "", xml)
    # Extract the content portion of the XML
    root = ET.fromstring(xml)
    data = root.find(".//NewDataSet")
    if data:
        return ET.tostring(data)

def processId(outfile, id):
    logger.info('downloading id: {}'.format(id))
    for attempt in range(1, 4):
        try:
            content = reduceXml(download(id))
            if content:
                outfile.write(content)
                return
            else:
                logger.warn("no content for {} (attempt {})".format(id, attempt))
        except Exception as e:
            logger.warn("exception for {} (attempt {})".format(id, attempt), exc_info=True)
    logger.error("no content for {} after max tries".format(id))

def main():
    with open('idlist.txt', 'r') as idlist, open('raw.xml', 'w') as outfile:
        outfile.write("<ICTRP>\n")
        for id in idlist:
            processId(outfile, id.rstrip('\n'))
        outfile.write("</ICTRP>")

if __name__ == "__main__":
    main()
