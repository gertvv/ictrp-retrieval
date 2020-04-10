#!/usr/bin/python3
import sys
import os
import datetime
import json
from elasticsearch import Elasticsearch, RequestsHttpConnection

import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logging.getLogger('elasticsearch').setLevel(logging.WARN)

ch = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('[%(levelname)s] %(asctime)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

if (len(sys.argv) != 4):
    logger.error("Usage: ./es.py <mode> <index> <filename>")
    sys.exit(1)

mode = sys.argv[1]
index = sys.argv[2]
fname = sys.argv[3]

if (mode == '--aws'):
    from aws_requests_auth.aws_auth import AWSRequestsAuth

    es_host = os.environ['AWS_ES_HOST']
    auth = AWSRequestsAuth(aws_access_key=os.environ['AWS_ACCESS_KEY_ID'],
                           aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
                           aws_host=es_host,
                           aws_region=os.environ['AWS_DEFAULT_REGION'],
                           aws_service='es')

    # use the requests connection_class and pass in our custom auth class
    es = Elasticsearch(host=es_host,
                              port=80,
                              connection_class=RequestsHttpConnection,
                              http_auth=auth)
elif (mode == '--local'):
    es = Elasticsearch(host='localhost', port=9200, connection_class=RequestsHttpConnection)

print(es.info())

with open('mappings.json') as f: indexDef = f.read()

if (es.indices.exists(index=index)):
    res = es.indices.delete(index=index)
    if (not res['acknowledged']):
        logger.error("Could not delete index {}".format(index))
        raise "Failed to delete index"

res = es.indices.create(index=index, body=indexDef)
if (not res['acknowledged']):
    logger.error("Could not create index {}".format(index))
    raise "Failed to create index"

with open(fname, 'r') as f:
    lineNo = 0
    for l in f:
        if (lineNo % 1000 == 0):
            logger.info("Inserted {:,} records".format(lineNo))
        id = json.loads(l)['id']
        res = es.create(index=index, doc_type='record', id=id, body=l)
        if (res['result'] != 'created'):
            logger.error("Failed to create record for {}: {}".format(id, res))
        lineNo += 1
    logger.info("Inserted {:,} records".format(lineNo))
