#!/usr/bin/python3
import sys
import urllib.request, urllib.error, urllib.parse
import re

import xml.etree.cElementTree as ET

with open(sys.argv[1], 'r') as idlist:
    for i in idlist:
        i = i.strip()
        url = 'https://clinicaltrials.gov/ct2/show/{}?displayXml=true'.format(i)
        try:
            request = urllib.request.urlopen(url)
            result = request.read()
            root = ET.fromstring(result)
            mainId = root.find('./id_info/nct_id').text
        except urllib.error.HTTPError as e:
            mainId = "Error {}".format(e.code)
        print("{},{}".format(i, mainId))
