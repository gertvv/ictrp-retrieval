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

LOG=`date +"download-s3-%G-w%V.log"`

su -c './download-records-s3.py > $LOG' ubuntu

su -c './s3upload.py $LOG' ubuntu
