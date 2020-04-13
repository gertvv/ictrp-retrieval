#!/usr/bin/python3
import sys
import urllib.request, urllib.error, urllib.parse
import re

with open(sys.argv[1], 'r') as idlist:
    for i in idlist:
        i = i.strip()
        url = 'https://clinicaltrials.gov/archive/{}'.format(i)
        request = urllib.request.urlopen(url)
        result = request.read()
        dates = re.findall('>([0-9]{4}_[0-9]{2}_[0-9]{2})<', result)
        print("{},{},{}".format(i, dates[0].replace('_', '-'), dates[-1].replace('_', '-')))
