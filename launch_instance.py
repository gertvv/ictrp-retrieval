import boto3
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    ec2 = boto3.resource('ec2')

    with open('env.sh') as e, open('cloud-init.sh') as f:
        script = e.read() +  f.read()

        instance = ec2.create_instances(
            ImageId='ami-060cde69', # Ubuntu 16.04
            MinCount=1,
            MaxCount=1,
            KeyName='ictrp',
            UserData=script,
            SecurityGroups=['launch-wizard-1'],
            InstanceType='t3.small',
            InstanceInitiatedShutdownBehavior='terminate')

        logging.info(instance[0])
        return instance[0].id
