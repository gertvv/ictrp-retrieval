ICTRP record retrieval
===

Retrieve and normalize records from the ICTRP. Requires access credentials.

Dependencies
---

Requires python 2.7. For AWS integration (not required), use:

apt install python-pip
pip install elasticsearch
pip install aws-requests-auth
pip install boto3

Environment variables
---

For compatibility, make sure the locale is set:

```
export LC_ALL=C.UTF-8
```

For interaction with the ICTRP services, set:
`ICTRP_LIST_USERNAME`, `ICTRP_LIST_PASSWORD`, `ICTRP_GET_USERNAME`, `ICTRP_GET_PASSWORD`

For elasticsearch, set
`AWS_ES_HOST`, `AWS_REGION`, `AWS_IAM_KEY_ID`, `AWS_IAM_KEY_SECRET`

AWS settings
---

For S3, set default.region in `~/.aws/config` and credentials in `~/.aws/credentials`.

Running
---

`./download-list-local.py` will create a text file with a list of records.

`./download-records-local.py` will download all records from `idlist.txt` and write them to `raw.xml`.

`./download-records-s3.py` will download a list of records, download each record, and upload them as gzipped XML file to AWS S3.

`./parse.py <file>` will parse the XML and produce normalized JSON, one JSON object per line.

`./es.py <file>` will take a file of JSON objects, and put them into a clean ElasticSearch index. It will delete the index if it already exists.
