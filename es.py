import sys
import os
import datetime
import json
from aws_requests_auth.aws_auth import AWSRequestsAuth
from elasticsearch import Elasticsearch, RequestsHttpConnection

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
print es.info()

index = 'ictrp-{}-w{}'.format(*datetime.datetime.today().isocalendar())
with open('mappings.json') as f: indexDef = f.read()

if (es.indices.exists(index=index)):
    res = es.indices.delete(index=index)
    if (not res['acknowledged']): raise "Failed to delete index"

res = es.indices.create(index=index, body=indexDef)
if (not res['acknowledged']): raise "Failed to create index"

with open(sys.argv[1], 'r') as f:
    for l in f:
        id = json.loads(l)['id']
        res = es.create(index=index, doc_type='record', id=id, body=l)
        print "{}: {}".format(id, res['created'])
