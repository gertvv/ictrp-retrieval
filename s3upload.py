#!/usr/bin/python3
import sys
import boto3

s3 = boto3.resource('s3')
with open(sys.argv[1], 'rb') as f:
    object = s3.Bucket('ictrp-data').put_object(Key=sys.argv[1], Body=f)
    object.Acl().put(ACL='public-read')
