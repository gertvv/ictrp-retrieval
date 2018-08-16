#!/usr/bin/python
import sys
import json
import itertools
import tempfile
import gzip

import xml.etree.cElementTree as ET

from parseRecord import parseRecord

import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

ch = logging.StreamHandler(sys.stderr)
formatter = logging.Formatter('[%(levelname)s] %(asctime)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

def parseAll(f):
    text = ''
    for key,group in itertools.groupby(f, lambda l: '<NewDataSet ' in l or '</ICTRP>' in l):
        if key:
            line = list(group)[0]
            if '<NewDataSet' in line:
                text = '<NewDataSet xmlns:msdata="urn:schemas-microsoft-com:xml-msdata" xmlns:diffgr="urn:schemas-microsoft-com:xml-diffgram-v1">'
            else:
                text = '</ICTRP>'
        elif text != '':
            text = text + ''.join(group)
            print json.dumps(parseRecord(ET.fromstring(text)))

def main(argv):
    if argv[1] == '--s3':
        import boto3

        with tempfile.TemporaryFile() as tmpfile:
            s3 = boto3.client('s3')
            s3.download_fileobj('ictrp-data', argv[2], tmpfile)
            tmpfile.seek(0)
            with gzip.GzipFile(argv[2], 'r', 9, tmpfile) as f:
                parseAll(f)
    else:
        with gzip.open(argv[1], 'r') as f:
            parseAll(f)           

if __name__ == '__main__':
    main(sys.argv)
