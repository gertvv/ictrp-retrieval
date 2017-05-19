import logging
import sys
logger = logging.getLogger()
logger.setLevel(logging.INFO)

ch = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('[%(levelname)s] %(asctime)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

import listRecords

method1 = set(listRecords.ictrpList() + listRecords.nctList())
method2 = set(listRecords.crawlList())

print "From listing but not crawling: "
print "\n".join(sorted(method1 - method2))
print "From crawling but not listing: "
print "\n".join(sorted(method2 - method1))
