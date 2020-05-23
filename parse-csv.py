#!/usr/bin/python3
import csv
import sys
import json

# python parse-csv.py ICTRPWeek2March2020.csv | head -n 1 | jq .

path = ['id', 'NONE', 'secondary_ids', 'public_title', 'scientific_title', 'NONE', 'contacts/first_name', 'contacts/last_name', 'contacts/address', 'contacts/email', 'contacts/phone', 'contacts/affiliation', 'contacs/first_name', 'contacts/last_name', 'contacts/address', 'contacts/email', 'contacts/phone', 'contacts/affiliation', 'study_type', 'study_design', 'phase', 'date_registered', 'enrollment_date', 'target_size', 'recruitment_status', 'sponsors[is_primary=true]', 'sponsors[is_primary=false]', 'source_of_support', 'countries', 'health_conditions/description', 'interventions', 'eligibility_criteria_1', 'eligibility_criteria_2', 'outcomes[is_primary=true]', 'outcomes[is_primary=false]', 'NONE', 'NONE', 'NONE', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 'results/date_completed', '', '', '', '', '', '', '']

def cellAsList(val):
    val = val.strip()
    if val == 'NULL' or val == '':
        return []
    return val.split(';')

def parseListOfObjects(prefix, keys, row):
    vals = { k : cellAsList(row[path.index(prefix + k)]) for k in keys }
    objects = []
    l = max([ len(v) for v in vals.values() ])
    for i in range(l):
        objects.append({ k : (vals[k][i] if i < len(vals[k]) else None) for k in keys })
    return objects 

def parseContacts(row):
    keys = [ 'first_name', 'last_name', 'address',
        # 'city', 'country',
        'phone', 'email', 'affiliation' ];
    return parseListOfObjects('contacts/', keys, row)

def parseConditions(row):
    keys = [ 'description' ] # TODO: 'code'
    return parseListOfObjects('health_conditions/', keys, row)

def parseOutcomes(row):
    def outcome(isPrimary):
        return lambda val: {
            'description': val, # TODO
            'is_primary': True,
            'timeframe': None, # TODO
            'timepoints': None # TODO
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
    return map(lambda val: {
        'description': val, # TODO
        'code': None, # TODO
        'other_details': None # TODO
    }, cellAsList(row[path.index('interventions')]))

def parseCriteria(row):
    c1 = row[path.index('eligibility_criteria_1')]
    c2 = row[path.index('eligibility_criteria_2')]
    return {
        'text': (c1 if c1 != 'NULL' else '') + (c2 if c2 != 'NULL' else ''),
        'agemin': None, # TODO
        'agemax': None, # TODO
        'sex': None # TODO
    }

def parseRecord(row):
    # TODO: standardization
    return {
        'id': row[path.index('id')],
        #'study_id': ...
        #'registry': ...
        #'last_updated':  ...
        'date_registered': row[path.index('date_registered')], # TODO: standardize
        'public_title': row[path.index('public_title')],
        'scientific_title': row[path.index('scientific_title')],
        #'acronym': row[path.index('acronym')],
        'enrollment_date': row[path.index('enrollment_date')],
        'target_size': row[path.index('target_size')],
        'recruitment_status': row[path.index('recruitment_status')],
        'study_type': row[path.index('study_type')],
        'study_design': row[path.index('study_design')],
        #'allocation': row[path.index('allocation')],
        #'assignment': row[path.index('assignment')],
        'phase': row[path.index('phase')],
        'countries': cellAsList(row[path.index('countries')]), # TODO: standardize
        'contacts': parseContacts(row),
        'eligibility_criteria': parseCriteria(row),
        'health_conditions': parseConditions(row),
        'interventions': parseInterventions(row),
        'outcomes': parseOutcomes(row),
        'secondary_ids': cellAsList(row[path.index('secondary_ids')]),
        'source_of_support': row[path.index('source_of_support')],
        'sponsors': parseSponsors(row),
        #'results': row[path.index('results')],
        #'ethics_review': row[path.index('ethics_review')]
    }

def main(argv):
    with open(argv[1]) as csvFile:
        reader = csv.reader(csvFile)
        for row in reader:
            if len(row) > len(path):
                raise Exception('Unexpected number of columns %i / %i' % (len(row), len(path)))
            json.dump(parseRecord(row), sys.stdout)
            print()

if __name__ == '__main__':
    main(sys.argv)
