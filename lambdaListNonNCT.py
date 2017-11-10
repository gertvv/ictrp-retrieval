import boto3
import logging
import json
import datetime
import tempfile

logger = logging.getLogger()
logger.setLevel(logging.INFO)

import listRecords

def lambda_handler(event, context):
    bucket = 'ictrp-data'
    key = 'idlist/ictrp-idlist-non-nct-{}.txt'.format(datetime.datetime.today().strftime('%Y%m%d'))
    idlist = listRecords.ictrpList()
    with tempfile.TemporaryFile() as tmpfile:
      for id in idlist:
        tmpfile.write('{}\n'.format(id))
      tmpfile.seek(0)
      s3 = boto3.resource('s3')
      object = s3.Bucket(bucket).put_object(Key=key, Body=tmpfile)
      object.Acl().put(ACL='public-read')
      return '{}/{}/{}'.format('https://s3.eu-central-1.amazonaws.com', bucket, key)