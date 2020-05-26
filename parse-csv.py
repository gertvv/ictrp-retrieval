#!/usr/bin/python3
import csv
import sys
import json

from parseRecord import stdDateRegistered, registries, toTrialId
from stdCountries import stdCountries

# python parse-csv.py ICTRPWeek2March2020.csv | head -n 1 | jq .

# Note: NONE indicates column should not be mapped, empty indicates mapping is not known
path = [
    # A-E
    'id', 'NONE', 'secondary_ids', 'public_title', 'scientific_title',
    # F-J
    'NONE', 'contacts/first_name', 'contacts/last_name', 'contacts/address', 'contacts/email',
    # K-O
    'contacts/phone', 'contacts/affiliation', 'contacs/first_name', 'contacts/last_name', 'contacts/address',
    # P-T
    'contacts/email', 'contacts/phone', 'contacts/affiliation', 'study_type', 'study_design',
    # U-Y
    'phase', 'date_registered', 'enrollment_date', 'target_size', 'recruitment_status',
    # Z-AD
    'sponsors[is_primary=true]', 'sponsors[is_primary=false]', 'source_of_support', 'countries', 'health_conditions/description',
    # AE-AI
    'interventions', 'eligibility_criteria_1', 'eligibility_criteria_2', 'outcomes[is_primary=true]', 'outcomes[is_primary=false]',
    # AJ-AN
    'NONE', 'NONE', 'NONE', '', '',
    # AO-AS
    '', 'results/href', '', 'results/date_posted', '',
    # AT-AX
    '', '', '', '', '',
    # AY-BC
    '', '', 'results/date_completed', 'results/posted', 'ethics_review/status',
    # BD-BH
    'ethics_review/approval_date', 'ethics_review/contact_name', 'ethics_review/contact_address', 'ethics_review/contact_phone', 'ethics_review/contact_email'
]

# Fields known to be missing from CSV: see util/diff.py

def cellAsList(val):
    val = val.strip()
    if val == 'NULL' or val == '':
        return []
    return val.split(';')

def parseValue(val):
    return '' if val == 'NULL' else val

def parseObject(prefix, keys, row):
    return { k : parseValue(row[path.index(prefix + k)]) for k in keys }

def parseListOfObjects(prefix, keys, row):
    vals = { k : cellAsList(row[path.index(prefix + k)]) for k in keys }
    objects = []
    l = max([ len(v) for v in vals.values() ])
    for i in range(l):
        objects.append({ k : (vals[k][i] if i < len(vals[k]) else '') for k in keys })
    return objects 

def parseContacts(row):
    keys = [ 'first_name', 'last_name', 'address',
        'phone', 'email', 'affiliation' ];
    return parseListOfObjects('contacts/', keys, row)[::-1]

def parseConditions(row):
    condition = lambda val: {
        'description': val,
        'code': ''
    }
    return list(map(condition, cellAsList(row[path.index('health_conditions/description')])))

def parseOutcomes(row):
    def outcome(isPrimary):
        return lambda val: {
            'description': val, # TODO: sanitize
            'is_primary': isPrimary,
            'timepoints': '' # Not available
        }
    primary = map(outcome(True), cellAsList(row[path.index('outcomes[is_primary=true]')]))
    secondary = map(outcome(False), cellAsList(row[path.index('outcomes[is_primary=false]')]))
    return list(primary) + list(secondary)

def parseSponsors(row):
    def sponsor(isPrimary):
        return lambda val: {
            'name': val,
            'is_primary': isPrimary
        }
    primary = map(sponsor(True), cellAsList(row[path.index('sponsors[is_primary=true]')]))
    secondary = map(sponsor(False), cellAsList(row[path.index('sponsors[is_primary=false]')]))
    return list(primary) + list(secondary)

def parseInterventions(row):
    return list(map(lambda val: {
        'description': val, # TODO: sanitize
        'code': '', # Not available
        'other_details': '' # Not available
    }, cellAsList(row[path.index('interventions')])))

def parseCriteria(row):
    c1 = row[path.index('eligibility_criteria_1')]
    c2 = row[path.index('eligibility_criteria_2')]
    return {
        'text': (c1 if c1 != 'NULL' else '') + (c2 if c2 != 'NULL' else ''),
        'agemin': None, # TODO
        'agemax': None, # TODO
        'sex': None # TODO
    }

def parseRegistry(id):
    for reg in registries.values():
        if id.startswith(reg):
            return reg
    return None

def parseResults(row):
    return parseObject('results/', [ 'posted', 'date_posted', 'date_completed', 'href' ], row)

def parseEthicsReview(row):
    return parseObject('ethics_review/', [ 'status', 'approval_date', 'contact_name', 'contact_email', 'contact_address' ], row)

def parseRecord(row):
    id = row[path.index('id')]
    registry = parseRegistry(id)
    if registry == None:
        if (id.startswith('ACTRN')):
            registry = 'ANZCTR'
        else:
            raise Exception('No registry for %s' % id)
    countries = stdCountries(registry, cellAsList(row[path.index('countries')]))
    # TODO: standardization
    return {
        'id': id,
        'study_id': toTrialId(id),
        'registry': registry,
        'date_registered': stdDateRegistered(registry, row[path.index('date_registered')]),
        'public_title': row[path.index('public_title')],
        'scientific_title': row[path.index('scientific_title')],
        'enrollment_date': row[path.index('enrollment_date')],
        'target_size': row[path.index('target_size')],
        'recruitment_status': row[path.index('recruitment_status')],
        'study_type': row[path.index('study_type')],
        'study_design': row[path.index('study_design')],
        'allocation': '',#row[path.index('allocation')],
        'assignment': '',#row[path.index('assignment')],
        'phase': row[path.index('phase')],
        'countries': countries['countries'],
        'countries_non_standard': countries['unmatched'],
        'contacts': parseContacts(row),
        'eligibility_criteria': parseCriteria(row),
        'health_conditions': parseConditions(row),
        'interventions': parseInterventions(row),
        'outcomes': parseOutcomes(row),
        'secondary_ids': cellAsList(row[path.index('secondary_ids')]),
        'source_of_support': row[path.index('source_of_support')],
        'sponsors': parseSponsors(row),
        'results': parseResults(row),
        'ethics_review': parseEthicsReview(row)
    }

def main(argv):
    with open(argv[1], encoding='utf-8-sig') as csvFile:
        reader = csv.reader(csvFile)
        i = 0
        for row in reader:
            i = i + 1
            if len(row) > len(path):
                raise Exception('Unexpected number of columns %i / %i' % (len(row), len(path)))
            if len(row) < len(path):
                print('Unexpected number of columns %i / %i on line %i' % (len(row), len(path), i), file=sys.stderr)
                continue
            json.dump(parseRecord(row), sys.stdout)
            print()

if __name__ == '__main__':
    main(sys.argv)
