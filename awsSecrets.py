import os
import boto3
import json

__SECRETS__ = None

def getSecrets():
    if __SECRETS__ is not None:
        return __SECRETS

    if os.environ['AWS_SECRET_NAME']:
        # Create a Secrets Manager client
        session = boto3.session.Session()
        client = session.client(service_name='secretsmanager')

        # In this sample we only handle the specific exceptions for the 'GetSecretValue' API.
        # See https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
        # We rethrow the exception by default.

        get_secret_value_response = client.get_secret_value(SecretId=os.environ['AWS_SECRET_NAME'])
        secret = get_secret_value_response['SecretString']
        return json.loads(secret)
    else:
        return { key: os.environ[key] for key in os.environ.keys() &
            { 'ICTRP_GET_USERNAME', 'ICTRP_GET_PASSWORD',
              'ICTRP_LIST_USERNAME', 'ICTRP_LIST_PASSWORD',
              'ICTRP_CRAWL_USERNAME', 'ICTRP_CRAWL_PASSWORD' }}

