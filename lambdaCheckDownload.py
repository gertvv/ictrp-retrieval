#!/usr/bin/python3
import boto3
import datetime
import dateutil.relativedelta as rd
from botocore.exceptions import ClientError

s3 = boto3.client('s3')
sns = boto3.client('sns')

def keySize(key):
    try:
        response = s3.head_object(Bucket='ictrp-data', Key=key)
        return '{:0.1f}'.format(response['ContentLength'] / (1024.0 * 1024))
    except ClientError:
        return None

def lambda_handler(event, context):
    today = datetime.datetime.today()
    weekago = today - rd.relativedelta(days=7)
    dataset0 = 'ictrp-raw-{}-w{:02d}.xml.gz'.format(*weekago.isocalendar())
    dataset1 = 'ictrp-raw-{}-w{:02d}.xml.gz'.format(*today.isocalendar())

    msg = '{}: {}\n{}: {}\n'.format(dataset0, keySize(dataset0), dataset1, keySize(dataset1))

    sns.publish(TopicArn='arn:aws:sns:eu-central-1:743731058442:ictrp',
        Message=msg,
        Subject='ICTRP download result')
