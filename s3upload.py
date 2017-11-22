#!/usr/bin/python
import sys
import boto3

s3 = boto3.resource('s3')
object = s3.Bucket('ictrp-data').upload_file(sys.argv[1], sys.argv[1])
object.Acl().put(ACL='public-read')
