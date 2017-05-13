import sys
import os
import datetime
import json
from aws_requests_auth.aws_auth import AWSRequestsAuth
from elasticsearch import Elasticsearch, RequestsHttpConnection

es_host = os.environ['AWS_ES_HOST']
auth = AWSRequestsAuth(aws_access_key=os.environ['AWS_IAM_KEY_ID'],
                       aws_secret_access_key=os.environ['AWS_IAM_KEY_SECRET'],
                       aws_host=es_host,
                       aws_region=os.environ['AWS_REGION'],
                       aws_service='es')

# use the requests connection_class and pass in our custom auth class
es = Elasticsearch(host=es_host,
                   port=80,
                   connection_class=RequestsHttpConnection,
                   http_auth=auth)
print es.info()

index = 'ictrp-{}-w{}'.format(*datetime.datetime.today().isocalendar())
res = es.search(index=index, doc_type='record', body='{ "query": { "query_string": { "query": "public_title:diabetes" } } }')
print(res)
