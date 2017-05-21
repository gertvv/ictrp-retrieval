#!/usr/bin/python
import sys
import boto3

s3 = boto3.resource('s3')
s3.Bucket('ictrp-data').download_file(sys.argv[1], sys.argv[1])
