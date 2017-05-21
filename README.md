ICTRP record retrieval
===

Retrieve and normalize records from the ICTRP. Requires access credentials.

Why is this necessary?
---

There is no straightforward way to download the full set of records from the ICTRP.
Several methods of downloading exist, but there are problems with each of them.

### Crawler pages

The crawler pages link to an HTML page for each trial, and the trial ID can be extracted from the URL.
However, the list is unreliable. For example, on 2017-05-19, the following problems were detected:

 - Record EUCTR2013-001888-23-DK exists in the database, but page 17 ends at EUCTR2013-001888-23-DE and page 18 starts at From EUCTR2013-001888-23-GB, so it is not listed.
 - Page 73 is the final page, and ends at TCTR20160618001. However, 424 records exist beyond this: TCTR20160621001, ..., TCTR20170422002.

### GetTrials and GetTrialDetails services

The GetTrials service returns an XML document containing some basic information on each trial.
However, the service does not list records from ClinicalTrials.gov.

GetTrialDetails returns an XML record describing the requested trial. The service is not entirely reliable, and on occassion returns empty content for records that exist. It will also return empty content with no error code for records that do not exist. The XML does not include the "prospective registration" field, and does not list which other records the ICTRP considers duplicates.

### Querying ClinicalTrials.gov

Another set of IDs can be obtained by querying ClinicalTrials.gov - but this may return records not yet indexed by the ICTRP, and there may also be records listed by the ICTRP that are no longer listed on ClinicalTrials.gov.

### Advanced search

It is possible to download a list of records from the Advanced Search page in XML format (choose 'ALL' recruitment status and set no other query terms). However this list omits duplicates, and the XML format has a number of shortcomings, most seriously that values from arrays are concatenated into semi-colon separated strings, without taking into account semi-colons in the source strings. Fetching the data automatically is also made difficult by several layers of forms to go through. In addition, as of 2017-05-21, this method did not funtion for several weeks.

License
---

This repository is made available under the [MIT license](https://opensource.org/licenses/MIT) - see LICENSE.txt.

Dependencies
---

Requires python 2.7. For AWS integration (not required), use:

```
apt install python-pip
pip install elasticsearch
pip install aws-requests-auth
pip install boto3
```

Environment variables
---

For compatibility, make sure the locale is set:

```
export LC_ALL=C.UTF-8
```

For interaction with the ICTRP services, set:
`ICTRP_LIST_USERNAME`, `ICTRP_LIST_PASSWORD`, `ICTRP_GET_USERNAME`, `ICTRP_GET_PASSWORD`

For AWS access, set`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, and `AWS_DEFAULT_REGION`.
For ElasticSearch, set `AWS_ES_HOST`.

Running
---

`./download-list-local.py` will create a text file with a list of records.

`./download-records-local.py` will download all records from `idlist.txt` and write them to `raw.xml`.

`./download-records-s3.py` will download a list of records, download each record, and upload them as gzipped XML file to AWS S3.

`./parse.py <file>` will parse the XML and produce normalized JSON, one JSON object per line.

`./es.py <file>` will take a file of JSON objects, and put them into a clean ElasticSearch index. It will delete the index if it already exists.
