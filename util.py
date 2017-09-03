import re

# ChiCTR records may (very rarely) contain invalid XML entities
# The following were seen: &#x2;, &#x8;, ^#xB;, &#x1F;
def stripInvalidXmlEntities(xml):
    return re.sub("&#x([0-8BCEF]|1[0-9A-F]);", "", xml)
