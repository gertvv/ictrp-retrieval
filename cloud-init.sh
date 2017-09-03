#!/bin/bash

set -e # exit on error

export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get upgrade -y
apt-get install -y python-pip

pip install elasticsearch
pip install aws-requests-auth
pip install boto3

cd ~ubuntu

su -c 'git clone https://github.com/gertvv/ictrp-retrieval ictrp' ubuntu

cd ictrp

export LOG=`date +"download-s3-%G-w%V.log"`

# try to download records; don't exit on error
su -c './download-records-s3.py 2>&1 > $LOG' ubuntu || true

su -c './s3upload.py $LOG' ubuntu

shutdown -h now
