import unittest
import json
import re
from functools import reduce
import operator

import logging
logger = logging.getLogger()

def mangleCountryName(name):
    return re.sub("[\W]", "", name.lower())

isoCountries = {}
with open("countries-iso-3166.json") as f:
    isoCountries = dict((mangleCountryName(c["name"]), c) for c in json.load(f))
    parenthetical = re.compile("^([^\(]*) \(([^\)]*)\)$")
    paren = list(filter(lambda x: not not x[0], map(lambda c: [parenthetical.match(c["name"]), c], isoCountries.values())))
    for [m, c] in paren:
        isoCountries[mangleCountryName(m.groups()[1] + " " + m.groups()[0])] = c
    with open("countries-common-names.json") as g:
        for name, alt_names in json.load(g).items():
            for alt_name in alt_names:
                isoCountries[mangleCountryName(alt_name)] = isoCountries[mangleCountryName(name)]

def stdCountry(country):
    if not country.strip():
        return {}
    isoCountry = isoCountries.get(mangleCountryName(country))
    if not isoCountry:
        return { "unmatched": [ country ] }
    return { "countries": [ isoCountry["name"] ] }

def stdCountries(registry, countries):
    countries = list(filter(None, map(lambda x: x.strip(), countries)))
    if not countries:
        return { "countries": [], "unmatched": [] }
    if (registry == "SLCTR" or registry == "JPRN"):
        if (len(countries) > 1):
            logger.warn("Encountered {} record with > 1 country entry: {}".format(registry, countries))
        countries = reduce(operator.concat, map(lambda s: s.split(","), countries))
        if (registry ==  "SLCTR"):
            countries = reduce(lambda a, b: a[:-1] + [a[-1] + "," + b] if len(b) > 0 and b[0] == " " else a + [b], countries, [])
        countries = list(map(lambda x: x.strip(), countries))
    result = list(map(stdCountry, countries))
    def collect(prop):
        return reduce(operator.concat, map(lambda x: x.get(prop) if x.get(prop) else [], result), [])
    result = { "countries": collect("countries"), "unmatched": collect("unmatched") }
    return result

class TestStdCountry(unittest.TestCase):
    def test_exact_match(self):
        self.assertEqual(stdCountry("Afghanistan"), { "countries": ["Afghanistan"] })
        self.assertEqual(stdCountry("Angola"), { "countries": ["Angola"]})
        self.assertEqual(stdCountry("Bosnia and Herzegovina"), { "countries": ["Bosnia and Herzegovina"]})
        self.assertEqual(stdCountry("Iran (Islamic Republic of)"), { "countries": ["Iran (Islamic Republic of)"]})

    def test_ignore_whitespace(self):
        self.assertEqual(stdCountry(" Afghanistan"), { "countries": ["Afghanistan"] })
        self.assertEqual(stdCountry("Angola "), { "countries": ["Angola"] })

    def test_remove_empty(self):
        self.assertEqual(stdCountry(""), {})
        self.assertEqual(stdCountry("  "), {})

    def test_alternate_format(self):
        self.assertEqual(stdCountry("Iran, Islamic Republic of"), { "countries": ["Iran (Islamic Republic of)"]})
        self.assertEqual(stdCountry("Iran, Islamic Republic Of"), { "countries": ["Iran (Islamic Republic of)"]})
        self.assertEqual(stdCountry("Islamic Republic of Iran"), { "countries": ["Iran (Islamic Republic of)"]})

    def test_not_a_country(self):
        self.assertEqual(stdCountry("Lollipopland"), { "unmatched": [ "Lollipopland" ]})
        self.assertEqual(stdCountry("Asia"), { "unmatched": [ "Asia" ]})
        self.assertEqual(stdCountry(",Outside"), { "unmatched": [ ",Outside" ]})

    def test_common_name(self):
        self.assertEqual(stdCountry("United States"), { "countries": ["United States of America"] })
        self.assertEqual(stdCountry("United Kingdom"), { "countries": ["United Kingdom of Great Britain and Northern Ireland"] })
        self.assertEqual(stdCountry("Iran"), { "countries": ["Iran (Islamic Republic of)"] })

class TestStdCountries(unittest.TestCase):
    def test_collect(self):
        self.assertEqual(stdCountries("NCT", ["United States", "Afghanistan", "Lollipopland", "Netherlands"]), { "countries": ["United States of America", "Afghanistan", "Netherlands"], "unmatched": ["Lollipopland"] })

    def test_split(self):
        self.assertEqual(stdCountries("SLCTR", ["United States,Afghanistan,Lollipopland,Netherlands"]), { "countries": ["United States of America", "Afghanistan", "Netherlands"], "unmatched": ["Lollipopland"] })
        self.assertEqual(stdCountries("SLCTR", ["Iran, Islamic Republic of"]), { "countries": ["Iran (Islamic Republic of)"], "unmatched": [] })
        self.assertEqual(stdCountries("SLCTR", ["Afghanistan,Iran, Islamic Republic of,Belarus"]), { "countries": ["Afghanistan", "Iran (Islamic Republic of)", "Belarus"], "unmatched": [] })
        self.assertEqual(stdCountries("SLCTR", ["Afghanistan,Belarus,Lollipopland"]), { "countries": ["Afghanistan", "Belarus"], "unmatched": ["Lollipopland"] })
        self.assertEqual(stdCountries("JPRN", ["Afghanistan,Iran,Islamic Republic of,Belarus"]), { "countries": ["Afghanistan", "Iran (Islamic Republic of)", "Belarus"], "unmatched": ["Islamic Republic of"] })

    def test_empty(self):
        self.assertEqual(stdCountries("JPRN", ["Japan", "", ""]), { "countries": [ "Japan" ], "unmatched": [] })
        self.assertEqual(stdCountries("JPRN", ["", ""]), { "countries": [], "unmatched": [] })

if __name__ == "__main__":
    unittest.main()
