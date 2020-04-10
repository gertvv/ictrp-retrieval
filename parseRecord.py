from datetime import datetime
from stdCountries import stdCountries
import sys

def toTrialId(id):
    if id.startswith("EUCTR"):
        return id[:19]
    else:
        return id

def textOf(elm):
    if (elm != None):
        return elm.text
    else:
        return ''

def stripHtml(text): # TODO
    return text

def parseContact(elem):
    contact = {}
    contact['first_name'] = textOf(elem.find('Firstname'))
    contact['last_name'] = textOf(elem.find('Lastname'))
    contact['address'] = textOf(elem.find('Address'))
    contact['city'] = textOf(elem.find('City'))
    contact['country'] = textOf(elem.find('Country'))
    contact['phone'] = textOf(elem.find('Telephone'))
    contact['email'] = textOf(elem.find('Email'))
    contact['affiliation'] = textOf(elem.find('Affiliation'))
    return contact

# Eligibility criteria can occur 0 or 1 time(s)
def parseCriteria(elem):
    if (elem != None):
        criteria = {}
        criteria['text'] = stripHtml(textOf(elem.find('Inclusion_criteria')))
        criteria['agemin'] = textOf(elem.find('Inclusion_agemin'))
        criteria['agemax'] = textOf(elem.find('Inclusion_agemax'))
        criteria['sex'] = textOf(elem.find('Inclusion_sex'))
        return criteria
    else:
        return { 'text': '', 'agemin': '', 'agemax': '', 'sex': '' }

def parseCondition(elem):
    return {
        'description': stripHtml(textOf(elem.find('Condition_FreeText'))),
        'code': textOf(elem.find('Condition_code'))
    }

def parseIntervention(elem):
    return {
        'description': stripHtml(textOf(elem.find('Intervention_FreeText'))),
        'code': textOf(elem.find('Intervention_code')),
        'other_details': textOf(elem.find('Other_details'))
    }

def parsePrimaryOutcome(elem):
    return {
        'is_primary': True,
        'description': stripHtml(textOf(elem.find('Outcome_Name'))),
        'timeframe': stripHtml(textOf(elem.find('Time_frame1'))), # TODO: \[Time Frame: (.*)\] -> $1
        'timepoints': textOf(elem.find('Timepoints'))
    }

def parseSecondaryOutcome(elem):
    return {
        'is_primary': False,
        'description': stripHtml(textOf(elem.find('Outcome_Name'))),
        'timeframe': stripHtml(textOf(elem.find('Time_frame2'))), # TODO: \[Time Frame: (.*)\] -> $1
        'timepoints': textOf(elem.find('Timepoints'))
    }

"""
(def illegal-secondary-ids
  #{"nil known" "not available" "nill known" "dpmcda" "study name" "mpc-***********"
    "new secondary id. please modify" "no secondary id" "pending" "incomplete"
    "***********" "there is no secondary id" "no sponsor"
    "no secondary ids" "non applicable" "no trial id" "nil secondary id"
    "nil know" "none available" "none known"
    "not yet available" "not aplicable" "not yet" "not registered" "not required"
    "not registered yet" "not applicable" "not have secondary id" "not applied"
    "this trial does not have a secondary id" "not assigned" "nothing" "not"
    "not applicable this study has not been registered with any other registry"})

; returns nil for often-seen obviously bad secondary IDs
(defn clean-secondary-id [xml]
  (let [sid (clojure.string/trim (text-of xml :SecondaryID))
        sid-std (clojure.string/trim (str-replace (.toLowerCase sid) #"[^a-z0-9 -]" ""))]
    (cond
      (< (count sid-std) 5) nil
      (re-matches #"^version" sid-std) nil
      (contains? illegal-secondary-ids sid-std) nil
      :else sid)))
"""
def parseSecondaryId(elem): # TODO: clean IDs
    return elem.find('SecondaryID').text

def parseSecondarySponsor(elem):
	return {
		'name': textOf(elem.find('Secondary_Sponsor')),
		'is_primary': False
	}


registries = {
    'ANZCTR': 'ANZCTR',
    'German Clinical Trials Register': 'DRKS',
    'EU Clinical Trials Register': 'EUCTR',
    'ISRCTN': 'ISRCTN',
    'JPRN': 'JPRN',
    'CRIS': 'CRIS',
    'ClinicalTrials.gov': 'NCT',
    'Netherlands Trial Register': 'NTR',
    'PACTR': 'PACTR',
    'REBEC': 'REBEC',
    'RPCEC': 'RPCEC',
    'TCTR': 'TCTR',
    'ChiCTR': 'ChiCTR',
    'IRCT': 'IRCT',
    'SLCTR': 'SLCTR',
    'CTRI': 'CTRI',
    'REPEC': 'REPEC'
}
# Map registry names to manageable shorthand
def stdRegistry(val): # TODO
    return registries[val]

# The last updated date is consistent between registries, format "19 May 2014"
def stdLastUpdatedDate(val):
    return datetime.strptime(val, '%d %B %Y').strftime('%Y-%m-%d')

"""
-- dd/MM/yyyy registries
UPDATE record SET date_registered_std = STR_TO_DATE(date_registered, "%d/%m/%Y") WHERE registry IN ( 'ANZCTR', 'German Clinical Trials Register', 'EU Clinical Trials Register', 'ISRCTN', 'JPRN', 'CRIS', 'ClinicalTrials.gov', 'Netherlands Trial Register', 'PACTR', 'REBEC', 'RPCEC', 'TCTR') ;
"""
dateRegisteredFormat = {
    'ANZCTR': '%d/%m/%Y',
    'DRKS': '%d/%m/%Y',
    'EUCTR': '%d/%m/%Y',
    'ISRCTN': '%d/%m/%Y',
    'JPRN': '%d/%m/%Y',
    'NCT': '%d/%m/%Y',
    'NTR': '%d/%m/%Y',
    'PACTR': '%d/%m/%Y',
    'REBEC': '%d/%m/%Y',
    'RPCEC': '%d/%m/%Y',
    'TCTR': '%d/%m/%Y',
    'ChiCTR': '%Y-%m-%d',
    'CRIS': '%Y-%m-%d',
    'IRCT': '%Y-%m-%d',
    'SLCTR': '%Y-%m-%d',
    'CTRI': '%d-%m-%Y',
    'REPEC': '%d/%m/%Y'
}
    
# The date registered has a registry-dependent format
def stdDateRegistered(reg, val): # TODO
    try: 
        return datetime.strptime(val, dateRegisteredFormat[reg]).strftime('%Y-%m-%d') if val != None else None
    except:
        sys.stderr.write("Date {} for {} does not match {}\n".format(val, reg, dateRegisteredFormat[reg]))
        raise

def parseResults(elem):
    results = {}
    results['posted'] = textOf(elem.find('results_yes_no'))
    results['date_posted'] = textOf(elem.find('results_date_posted'))
    results['date_completed'] = textOf(elem.find('results_date_completed'))
    results['href'] = textOf(elem.find('results_url_link'))
    return results

def parseEthicsReview(elem):
    ethics = {}
    ethics['status'] = textOf(elem.find('Status')) if elem else ''
    ethics['approval_date'] = textOf(elem.find('Approval_Date')) if elem else ''
    ethics['contact_name'] = textOf(elem.find('Contact_Name')) if elem else ''
    ethics['contact_email'] = textOf(elem.find('Contact_Email')) if elem else ''
    ethics['contact_address'] = textOf(elem.find('Contact_Address')) if elem else ''
    return ethics

def parseRecord(root):
    registry = stdRegistry(textOf(root.find('./Trial/Primary_Register_text')))
    record = {}
    record['id'] = textOf(root.find('./Trial/TrialID'))
    record['study_id'] = toTrialId(record['id'])
    record['registry'] = registry
    record['last_updated'] = stdLastUpdatedDate(textOf(root.find('./Trial/last_updated')))
    record['date_registered'] = stdDateRegistered(registry, textOf(root.find('./Trial/Date_registration2')))
    record['public_title'] = textOf(root.find('./Trial/Public_title'))
    record['scientific_title'] = textOf(root.find('./Trial/Scientific_title'))
    record['acronym'] = textOf(root.find('./Trial/Acronym'))
    record['enrollment_date'] = textOf(root.find('./Trial/Date_enrollement')) # TODO: standardize
    record['target_size'] = textOf(root.find('./Trial/Target_size'))
    record['recruitment_status'] = textOf(root.find('./Trial/Recruitment_status2'))
    record['study_type'] = textOf(root.find('./Trial/Study_type'))
    record['study_design'] = stripHtml(textOf(root.find('./Trial/Study_design')))
    record['allocation'] = stripHtml(textOf(root.find('./Trial/Allocation')))
    record['assignment'] = stripHtml(textOf(root.find('./Trial/Assignement')))
    record['phase'] = textOf(root.find('./Trial/Phase'))
    countries = stdCountries(registry, map(lambda c: textOf(c.find('./CountryName')), root.iter('Country')))
    record['countries'] = countries['countries']
    record['countries_non_standard'] = countries['unmatched']
    record['contacts'] = list(map(parseContact, root.iter('Contacts')))
    record['eligibility_criteria'] = parseCriteria(root.find('./Criteria'))
    record['health_conditions'] = list(map(parseCondition, root.iter('Health_condition')))
    record['interventions'] = list(map(parseIntervention, root.iter('Intervention')))
    record['outcomes'] = list(map(parsePrimaryOutcome, root.iter('Primary_outcome'))) + list(map(parseSecondaryOutcome, root.iter('Secondary_outcome')))
    record['secondary_ids'] = [i for i in map(parseSecondaryId, root.iter('Secondary_IDs'))if not i is None]
    record['source_of_support'] = textOf(root.find('./Source_support/Source_Name')) # TODO: check only 1 can exist
    record['sponsors'] = [ { 'name': textOf(root.find('./Trial/Primary_sponsor')), 'is_primary': True } ] + list(map(parseSecondarySponsor, root.iter('Secondary_Sponsors')))
    record['results'] = parseResults(root.find('./Results'))
    record['ethics_review'] = parseEthicsReview(root.find('./Ethics_review'));
    return record
