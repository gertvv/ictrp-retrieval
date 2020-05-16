import os
import urllib.request, urllib.error, urllib.parse
import logging
import time

logger = logging.getLogger()

urlTemplate = "http://apps.who.int/trialsearch/TrialService.asmx/GetTrialDetails?TrialIDnum={id}&username={username}&password={password}"

from util import stripInvalidXmlEntities

import awsSecrets
ICTRP_SECRETS = awsSecrets.getSecrets()

# Read binary to preserve \r\n endings
with open('expect_header.txt', 'r') as f:
    expectedHeader = f.read()
with open('expect_footer.txt', 'r') as f:
    expectedFooter = f.read()
with open('empty_footer.txt', 'r') as f:
    emptyFooter = f.read()

def download(id):
    url = urlTemplate.format(id=id,
        username=ICTRP_SECRETS['ICTRP_GET_USERNAME'],
        password=ICTRP_SECRETS['ICTRP_GET_PASSWORD'])
    request = urllib.request.urlopen(url, timeout=60)
    response = request.read().decode('utf-8')
    request.close()
    return response

class XmlSchemaChanged(Exception):
    pass

def reduceXml(xml):
    # Convert newlines and add a trailing newline for sanity
    xml = xml.replace('\r\n', '\n') + '\n'
    # Check if XML contains no content. This may indicate the record does not
    # exist, or that it is temporarily not being returned
    if xml.endswith(emptyFooter): return ""
    # Check header and footer are as expected
    if not xml.startswith(expectedHeader): raise XmlSchemaChanged("Header did not match")
    if not xml.endswith(expectedFooter): raise XmlSchemaChanged("Footer did not match")
    # Extract the content portion of the XML
    xml = xml[len(expectedHeader):-len(expectedFooter)]
    xml = stripInvalidXmlEntities(xml)
    return xml

def processId(outfile, id):
    logger.info('downloading id: {}'.format(id))
    for attempt in range(1, 4):
        try:
            content = reduceXml(download(id))
            if content:
                outfile.write(content.encode('utf-8'))
                return True
            else:
                logger.warn("no content for {} (attempt {})".format(id, attempt))
        except XmlSchemaChanged as e:
            raise e
        except Exception as e:
            logger.warn("exception for {} (attempt {})".format(id, attempt), exc_info=True)
    logger.error("no content for {} after max tries".format(id))
    return False

def downloadRecords(idlist, outfile, pauseForAttempt3=False):
    outfile.write(b'<ICTRP xmlns:msdata="urn:schemas-microsoft-com:xml-msdata" xmlns:diffgr="urn:schemas-microsoft-com:xml-diffgram-v1">\n')
    # attempt 1
    failed = [id for id in idlist if not processId(outfile, id)]
    logger.info('failed on attempt 1: {} records'.format(len(failed)))
    if len(failed) == 0:
        outfile.write(b'</ICTRP>')
        return []
    # attempt 2
    idlist = failed
    failed = [id for id in idlist if not processId(outfile, id)]
    logger.info('failed on attempt 2: {} records'.format(len(failed)))
    if len(failed) == 0:
        outfile.write(b'</ICTRP>')
        return []
    # attempt 3
    if pauseForAttempt3:
        logger.info('waiting 15 minutes to retry third time')
        time.sleep(15*60)
    idlist = failed
    failed = [id for id in idlist if not processId(outfile, id)]
    logger.info('failed on attempt 3: {} records'.format(len(failed)))
    outfile.write(b'</ICTRP>')
    return failed
