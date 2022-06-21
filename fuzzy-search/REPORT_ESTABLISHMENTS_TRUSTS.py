import sys
import importlib.util
import subprocess
import time
import requests

try:
    import math 
except ImportError:
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'math'])
    print(f'math installed successfully')
    import math 

try:
    import pandas as pd
except ImportError:
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pandas'])
    print(f'pandas installed successfully')
    import pandas as pd

try:
    from simple_salesforce import Salesforce
except ImportError:
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'simple_salesforce'])
    print(f'simple_salesforce installed successfully')
    from simple_salesforce import Salesforce
    
try:
    from fuzzywuzzy import fuzz
except ImportError:
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'fuzzywuzzy'])
    print(f'fuzzywuzzy installed successfully')
    from fuzzywuzzy import fuzz

try:
    from tqdm import tqdm
except ImportError:
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'tqdm'])
    print(f'tqdm installed successfully')
    from tqdm import tqdm
    
try:
    import pwinput
except ImportError:
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pwinput'])
    print(f'pwinput installed successfully')
    import pwinput
    
    
def find_CEO(CEO = None, trust = None, trust_list = None, contacts = None, bar = None):
    """
    Given a CEO name as a string, attempts to match the CEO against a member on Salesforce using their name and school data.
    Returns the index position from the Salesforce dataframe for a match.
    
    Args:
    - CEO: A string corresponding to the name of the CEO
    - trust: A string corresponding to the trust the CEO belongs to
    - trust_list: A dataframe of all establishments and the trust they belong to
    - contacts: A dataframe of all members on Salesforce
    - bar: A tqdm object for showing progress on iterations
    """
    if bar:
        bar.update(1) # increment progress bar
    # prepare CEO name and establishment as a pattern for more efficient fuzzy search and match
    # also filters out tokens smaller than 2 chars which slightly aids efficiency (eg. 'de' and 'desmond')
    ceo_pattern = '|'.join([str(x)  for x in str(CEO).split() if len(x)>2])
    ceo_pattern = f'{ceo_pattern}'
    ests = trust_list[trust_list['establishment_group']==trust]['school_name'].values.tolist()
    ests.append(trust)
    # initialise results variables
    best = 0
    best_index = None
    # iterate all establishment potential matches, score using fuzzy match, return the index of best match
    for est in ests:
        # prepare establishment name as a pattern for more efficient fuzzy search and match
        # also removes common words
        e_pattern = '|'.join(str(est).split()).replace('school','').replace('community','').replace('academy','').replace(' of ','').replace('the ','').replace(' the','').replace(' and ','').replace(' for ','')
        e_pattern = e_pattern.replace('college','').replace('girls','').replace('boys','').replace('primary','').replace('secondary','').replace('high','')
        e_pattern = f'{e_pattern}'
        try:
            for index, person in zip(contacts[(contacts['Name'].str.contains(ceo_pattern))&
                (contacts['School_Name__c'].str.contains(e_pattern))][['Name','School_Name__c']].index, 
                                     contacts[(contacts['Name'].str.contains(ceo_pattern))&
                (contacts['School_Name__c'].str.contains(e_pattern))][['Name','School_Name__c']].values):
                p = f'{person[0]}' # score name
                m = f'{str(CEO)}'
                score = fuzz.ratio(m, p)
                p = f'{person[1]}' # score establishment
                m = f'{str(est)}'
                score += fuzz.ratio(m, p) 
                score = score/2 # average result
                if score > 80 and (score > best or best == None):
                    best = score
                    best_index = index
            return best_index
        except:
            return best_index
        
    
def ceo_index_contacts(group_name = None, contacts = None, trust_list = None):
    """
    Returns the member index of a ceo to another dataframe.
    """
    if group_name is not None:
        return trust_list[trust_list['Group name']==group_name]['CEO_member_index'].values
    else:
        return None
    

def extract_ht(index = None, contacts = None, field = None):
    """
    Uses member index to extract first name from found member
    """
    if index is not None:
        return CONTACTS.loc[index, field]
    else:
        return None
    
    
def extract_ceo(CONTACTS, TRUSTS, RESULTS):
    """
    Uses the index found, extracts and applied to RESULTS df. Then uses the index to extract name and other details from CONTACTS
    """
    # Index position in CONTACTS
    RESULTS['CEO_member_index'] = RESULTS.apply(lambda x: ceo_index_contacts(group_name = x['establishment_group'],
                                                                             contacts = CONTACTS,
                                                                             trust_list = TRUSTS), axis=1)
    # Name
    RESULTS['CEO_name'] = RESULTS.apply(lambda x: extract_ht(index = x['CEO_member_index'],
                                                                contacts = CONTACTS,
                                                                field = 'Name'), axis =1)
    # type
    RESULTS['CEO_type'] = RESULTS.apply(lambda x: extract_ht(index = x['CEO_member_index'],
                                                                contacts = CONTACTS,
                                                                field = 'MemberType__c'), axis =1)
    # status
    RESULTS['CEO_status'] = RESULTS.apply(lambda x: extract_ht(index = x['CEO_member_index'],
                                                                contacts = CONTACTS,
                                                                field = 'Member_Status__c'), axis =1)
    # email
    RESULTS['CEO_email'] = RESULTS.apply(lambda x: extract_ht(index = x['CEO_member_index'],
                                                                contacts = CONTACTS,
                                                                field = 'Email'), axis =1)
    return RESULTS
    

def ceo_in_membership(RESULTS, TRUSTS, CONTACTS):
    """
    Identifies any trust CEOs within Salesforce membership data
    """
    print('Finding CEOs in membership...')
    with tqdm(total=CEO_list.shape[0]) as pbar:
        TRUSTS['CEO_member_index'] = TRUSTS.apply(lambda x: find_CEO(CEO = x['Name'], 
                                                              trust = x['Group name'], 
                                                              trust_list = RESULTS, 
                                                              contacts = CONTACTS, 
                                                              bar = pbar), axis=1)
    pbar.close()
    # extract data via index in TRUSTS to member in CONTACTS, results in RESULTS
    RESULTS = extract_ceo(CONTACTS, TRUSTS, RESULTS)
    return RESULTS
    
    
def find_headteacher(head = None, establishment = None, contacts = None, bar = None):
    """
    Takes a dataframe of all establishments and their headteacher data and searches membership data from Salesforce for matches.
    Returns the index position of the member from Salesforce
    
    Args:
    - head: A string corresponding to the name of the headteacher to search for
    - establishment: A dataframe containing the DfE establishments data
    - contacts: A dataframe containing membership data from Salesforce
    - bar: A tqdm object for monitoring iteration progress
    """
    if bar:
        bar.update(1) # increment progress bar
    # convert headteacher name and establishment strings into a pattern for more efficient matching/searching
    h_pattern = '|'.join([x  for x in head.split() if len(x)>2])
    h_pattern = f'{h_pattern}'
    e_pattern = '|'.join(str(establishment).split()).replace('school','').replace('community','').replace('academy','').replace(' of ','').replace('the ','').replace(' the','').replace(' and ','').replace(' for ','')
    e_pattern = e_pattern.replace('college','').replace('girls','').replace('boys','').replace('primary','').replace('secondary','').replace('high','')
    e_pattern = f'{e_pattern}'
    # initialise results variables
    best = 0
    best_index = None
    # iterate over possible matches, scoring using fuzzy matching, returning the best match or None
    for index, person in zip(contacts[(contacts['Name'].str.contains(h_pattern))&
        (contacts['School_Name__c'].str.contains(e_pattern))][['Name','School_Name__c']].index, 
                             contacts[(contacts['Name'].str.contains(h_pattern))&
        (contacts['School_Name__c'].str.contains(e_pattern))][['Name','School_Name__c']].values):
        p = f'{person[0]}' # score name
        m = f'{head}'
        score = fuzz.ratio(m, p)
        p = f'{person[1]}' # score establishment
        m = f'{establishment}'
        score += fuzz.ratio(m, p)
        score = score/2 # average result
        if score > 80 and (score > best or best == None):
            best = score
            best_index = index
    return best_index
    
    
def heads_in_membership(RESULTS, CONTACTS):
    """
    Given a headteacher name and school, attempts to find the person in membership using fuzzy search
    """
    # Match headteachers against Salesforce data
    print('Matching headteachers against membership data...')
    with tqdm(total=RESULTS.shape[0]) as pbar:
        RESULTS['head_member_index'] = RESULTS.apply(lambda x: find_headteacher(head = x['establishment_head'], 
                                                                  establishment = x['matched_establishment'], 
                                                                  contacts = CONTACTS, bar = pbar), axis=1)
    pbar.close()
    
    # Extract other data from Contacts into RESULTS
    # name
    print('Extracting headteacher names...')
    RESULTS['headteacher_name'] = RESULTS.apply(lambda x: extract_ht(index = x['head_member_index'], 
                                                                     contacts = CONTACTS,
                                                                     field = 'Name'), axis=1)
    # type
    print('Extracting headteacher types...')
    RESULTS['headteacher_type'] = RESULTS.apply(lambda x: extract_ht(index = x['head_member_index'], 
                                                                     contacts = CONTACTS,
                                                                     field = 'MemberType__c'), axis=1)
    # status
    print('Extracting headteacher statuses...')
    RESULTS['headteacher_status'] = RESULTS.apply(lambda x: extract_ht(index = x['head_member_index'], 
                                                                     contacts = CONTACTS,
                                                                     field = 'Member_Status__c'), axis=1)
    # email
    print('Extracting headteacher email...')
    RESULTS['headteacher_email'] = RESULTS.apply(lambda x: extract_ht(index = x['head_member_index'], 
                                                                     contacts = CONTACTS,
                                                                     field = 'Email'), axis=1)
    return RESULTS
    
    
def est_index_finder(school = None, all_est = None, bar = None):
    """
    Match schools from membership data with schools from DfE education establishment data
    - Uses Fuzzy search and match algorithm for partial matching
    - Returns the index number of the matched establishment
    
    Args:
    - school: A string corresponding to the school name to match against DfE data
    - all_est: A pandas dataframe containing the csv establishment data from DfE
    - bar: A tqdm object for showing progress so far on iterations
    """
    if bar:
        bar.update(1) # increment progress bar
    if school is not None and all_est is not None:
        # remove some common words from the school string to speed up matching
        school_copy = school.replace('school','').replace('community','').replace('academy','').replace(' of ','').replace('the ','').replace(' the','').replace(' and ','').replace(' for ','')
        school_copy = school_copy.replace('college','').replace('girls','').replace('boys','').replace('primary','').replace('secondary','').replace('high','')
        if len(school_copy) == 0: # return None should the string be reduced to no tokens
            return None
        # Convert the school name into a pattern allowing conditional filtering matching one or more tokens
        pattern = '|'.join(str(school_copy).split())
        pattern = f'{pattern}'
        try:
            # Filters the establishments df to matches on the pattern
            ests = all_est[all_est['EstablishmentName'].str.contains(pattern)]['EstablishmentName'].values
            est_index = all_est[all_est['EstablishmentName'].str.contains(pattern)]['EstablishmentName'].index
            # Initialise results variables
            best = None
            best_index = None
            # Iterate over establishment matches and score using fuzzy matching
            for i,v in zip(est_index, ests):
                score = fuzz.ratio(school, v)
                if score > 80 and (best == None or score > best): # Only save > 80 and best scores
                    best = score
                    best_index = i
            return best_index
        except:
            return None
    
    
def extract_school(est_index, RESULTS, bar):
    """
    Uses index to extract establishment name
    """
    bar.update(1)
    if math.isnan(est_index) == False:
        return RESULTS.loc[est_index, 'EstablishmentName']
    else:
        return None
    

def member_count(school, CONTACTS, bar):
    """
    Counts number of active and overdue members with a specific school name
    """
    bar.update(1)
    return CONTACTS[(CONTACTS['School_Name__c']==school)&
                   (CONTACTS['Member_Status__c'].str.contains('active|overdue'))].shape[0]


def fellow_count(school, CONTACTS, bar):
    """
    Counts number of active and overdue Fellows with a specific school name
    """
    bar.update(1)
    return CONTACTS[(CONTACTS['School_Name__c']==school)&
                   (CONTACTS['Member_Status__c'].str.contains('active|overdue'))&
                   (CONTACTS['MemberType__c'].str.contains('fello'))].shape[0]


def ceip_count(school, ENROLMENTS, bar):
    """
    Counts number of active and overdue ceip members with a specific school name
    """
    bar.update(1)
    return sum(ENROLMENTS[(ENROLMENTS['course_name'].str.contains('certificate in evidence informed practic'))&
              (ENROLMENTS['school']==school)&
              (ENROLMENTS['status'].str.contains('active|overdue'))].groupby('name').sum().values>=4)


def cteach_count(school, ENROLMENTS, bar):
    """
    Counts number of active and overdue cteach members with a specific school name
    """
    bar.update(1)
    courses = ['Certificate in Evidence Informed Practic',
    'Candidate Registration for Chartered Teacher Statu',
    'Certificate in Evidence-Informed Practice NIE',
    'Professional Knowledge Awar',
    'Development of Teaching Practice Awar',
    'Certificate in Educational Research and Inquir',
    'Application for Chartered Teacher Statu']

    pattern = '|'.join([x.lower() for x in courses])
    return sum(ENROLMENTS[(ENROLMENTS['course_name'].str.contains(pattern))&
              ~(ENROLMENTS['course_name'].str.contains('leader'))&
              (ENROLMENTS['school']==school)&
              (ENROLMENTS['status'].str.contains('active|overdue'))].groupby('name').sum().values>=4)


def clead_count(school, ENROLMENTS, bar):
    """
    Counts number of active and overdue clead members with a specific school name
    """
    bar.update(1)
    return sum(ENROLMENTS[(ENROLMENTS['course_name'].str.contains('leader'))&
              (ENROLMENTS['school']==school)&
              (ENROLMENTS['status'].str.contains('active|overdue'))].groupby('name').sum().values>=4)
    
    
def members_in_establishments(RESULTS, CONTACTS, ENROLMENTS, OUTPUT_PREF):
    """
    Find the number of members per establishment using fuzzy search and match algorithm.
    """
    # Get list of schools from contacts data
    schools = CONTACTS[(CONTACTS['School_Name__c'].isna()==False)&
         (CONTACTS['Member_Status__c'].str.contains('active|overdue'))&
        ~(CONTACTS['School_Name__c']=='None')&
        ~(CONTACTS['School_Name__c']=='none')&
        ~(CONTACTS['School_Name__c']=='n/a')][['School_Name__c']].value_counts()
    schools = pd.DataFrame({'school_name':[str(x).replace('(','').replace(')',''
                                            ).replace(',','').replace('"',''
                                            ).replace("'",'') 
                                            for x in schools.index.tolist()], 
                                        'no_members':schools.values.tolist()})
    
    # Match member school data against DfE establishment data
    print('Matching contacts school data against establishments data...')
    with tqdm(total=schools.shape[0]) as pbar: 
        schools['est_index_match'] = schools.apply(lambda x: est_index_finder(school = x['school_name'], 
                                                                    all_est = RESULTS, bar=pbar), axis=1)
    pbar.close()
    
    # Infer identified establishment data onto CONTACTS
    print('Extracting establishment names...')
    with tqdm(total=schools.shape[0]) as pbar:
        schools['est_name'] = schools.apply(lambda x: extract_school(x['est_index_match'], RESULTS, pbar), axis=1)
    pbar.close()
    
    if OUTPUT_PREF[0] == True: # active and overdue member count
        print('Counting number of members per establishment...')
        with tqdm(total=schools.shape[0]) as pbar:
            schools['no_members'] = schools.apply(lambda x: member_count(x['school_name'], CONTACTS, pbar), axis=1)
            RESULTS['no_members'] = schools.groupby('est_name').sum()['no_members']
        pbar.close()
        
    if OUTPUT_PREF[1] == True: # active and overdue fellow count
        print('Counting number of fellows per establishment...')
        with tqdm(total=schools.shape[0]) as pbar:
            schools['no_fellows'] = schools.apply(lambda x: fellow_count(x['school_name'], CONTACTS, pbar), axis=1)
            RESULTS['no_fellows'] = schools.groupby('est_name').sum()['no_fellows']
        pbar.close()
        
    if OUTPUT_PREF[2] == True: # active and overdue ceip count
        print('Counting number of CEIP per establishment...')
        with tqdm(total=schools.shape[0]) as pbar:
            schools['no_ceip'] = schools.apply(lambda x: ceip_count(x['school_name'], ENROLMENTS, pbar), axis=1)
            RESULTS['no_ceip'] = schools.groupby('est_name').sum()['no_ceip']
        pbar.close()
        
    if OUTPUT_PREF[3] == True: # active and overdue cteach count
        print('Counting number of CTeachers per establishment...')
        with tqdm(total=schools.shape[0]) as pbar:
            schools['no_cteach'] = schools.apply(lambda x: cteach_count(x['school_name'], ENROLMENTS, pbar), axis=1)
            RESULTS['no_cteach'] = schools.groupby('est_name').sum()['no_cteach']
        pbar.close()
        
    if OUTPUT_PREF[4] == True: # active and overdue clead count
        print('Counting number of CLeaders per establishment...')
        with tqdm(total=schools.shape[0]) as pbar:
            schools['no_clead'] = schools.apply(lambda x: clead_count(x['school_name'], ENROLMENTS, pbar), axis=1)
            RESULTS['no_clead'] = schools.groupby('est_name').sum()['no_clead']
        pbar.close()
    return RESULTS
        
    
def run_reports(DIR_PATH, CONTACTS, ESTABLISHMENTS, TRUSTS, ENROLMENTS, OUTPUT_PREF):
    """
    Runs the chosen reports and saves them to files located in directory path.
    
    Args:
    - DIR_PATH: chosen output directory
    - CONTACTS: Contacts data from Salesforce
    - ESTABLISHMENTS: Data from DfE on all education establishments
    - TRUSTS: Data from DfE on all education trusts
    - OUTPUT_PREF: Preference on reports to run in this instance
    """
    # Create output dataframe data
    RESULTS = ESTABLISHMENTS.copy(deep=True)
    # Processing stage
    print('Processing:')
    
    if sum(OUTPUT_PREF[0:5]) >= 1: # if at least one is true
        # Run number of members, and/or fellows, cteachers in establishments report
        RESULTS = members_in_establishments(RESULTS, CONTACTS, ENROLMENTS, OUTPUT_PREF)
        
    if OUTPUT_PREF[5] == True:
        # Identify headteachers in membership
        RESULTS = heads_in_membership(RESULTS, CONTACTS)
        
    if OUTPUT_PREF[6] == True:
        # Identify CEOs in membership
        RESULTS = ceo_in_membership(RESULTS, TRUSTS, CONTACTS)
        
    # Saving results
    RESULTS.to_csv(f'{DIR_PATH}establishment_results.csv', index = False)
    
    
def output_preferences():
    """
    User choice of reports to process and output.
    """
    # Tick box options 
    output_pref = [True for x in range(0,7)]
    return output_pref

    
def download_dfe_data(DIR_PATH):
    """
    Reads the latest establishments and trusts data (csv) from get-information-schools.service.gov.uk
    - https://www.get-information-schools.service.gov.uk/
    """
    # import the file
    establishments = pd.read_csv(f'{DIR_PATH}establishments.csv')
    trusts = pd.read_csv(f'{DIR_PATH}trusts.csv')
    # turn all strings into lower case
    for col in establishments.columns:
        try:
            establishments[col] = establishments[col].str.lower()
        except:
            continue
    for col in trusts.columns:
        try:
            trusts[col] = trusts[col].str.lower()
        except:
            continue
    return establishments, trusts


def get_enrolment_data(sf):
    """
    Queries SF for enrolment data and returns a dataframe
    """
    # initialise results dataframe
    enrolment_data = pd.DataFrame({'name':[],
                                  'email':[],
                                  'school':[],
                                  'status':[],
                                  'm_type':[],
                                  'course_name':[]})
    
    # query SF for data
    query = "SELECT Enrolment_passed__c, Course__r.Name, Candidate__r.Name, Candidate__r.Email, Candidate__r.School_Name__c, Candidate__r.Member_Status__c, Candidate__r.MemberType__c  FROM Enrolment__c"
    enrols = sf.query_all(f'{query}')
    
    # process query data
    for contact in enrols['records']:
        passed = contact['Enrolment_passed__c']
        name = contact['Candidate__r']['Name']
        email = contact['Candidate__r']['Email']
        school = contact['Candidate__r']['School_Name__c']
        status = contact['Candidate__r']['Member_Status__c']
        m_type = contact['Candidate__r']['MemberType__c']
        course_name = contact['Course__r']['Name']
        row = pd.DataFrame({'name':name,
                           'email':email,
                           'school':school,
                           'status':status,
                           'm_type':m_type,
                           'course_name':course_name,
                           'passed':passed}, index=[1])
        enrolment_data = pd.concat([enrolment_data, row], ignore_index=True)
    
    # lower case all strings
    for col in enrolment_data.columns:
        try:
            enrolment_data[col] = enrolment_data[col].str.lower()
        except:
            continue
            
    return enrolment_data
    
    
def contact_fields():
    """
    Requests which Salesforce contact fields to report on
    """
    choice = "SELECT Name, Email, Member_Status__c, MemberType__c, School_Name__c FROM Contact"
    return choice

    
def download_SF_contacts_data():
    """
    Use SOQL to query Salesforce for data
    """
    # Login to Salesforce process 
    while True: 
        username, password, security_token = get_login()
        try:
            sf = process_login(username, password, security_token)
        except Exception as e:
            print(e)
        if sf:
            break
    # contact fields to report on
    query = contact_fields()
    # SOQL query 
    contacts = pd.DataFrame(sf.query_all(f'{query}')['records']).drop(columns=['attributes'])
    # turn all strings into lower-case
    for col in contacts.columns:
        try:
            contacts[col] = contacts[col].str.lower()
        except:
            continue
    enrols = get_enrolment_data(sf)
    for col in enrols.columns:
        try:
            enrols[col] = enrols[col].str.lower()
        except:
            continue
    return contacts, enrols


def process_login(username, password, security_token):
    """
    Login to Salesforce API for SOQL querying
    
    Args:
    - user: username for Salesforce account
    - passer: password for Salesforce account
    - coder: security token that allows API access
    """
    sf = Salesforce(
        username = username,
        password = password,
        security_token = security_token)
    print('Login successful')
    return sf


def get_login():
    """
    Requests user access details for logging into Salesforce via simple_salesforce API.
    """
    username = input('Email address: ')
    password = pwinput.pwinput(prompt='Password: ')
    security_token = pwinput.pwinput(prompt='Security token: ')
    return username, password, security_token


def setup_directory_path():
    """
    Directory path for program results output (csv)
    """
    # This section needs developing to be more user-friendly
    DIR_PATH = input('Enter the directory path in which to save results to: ')
    return DIR_PATH


def main():
    # Get directory path
    DIR_PATH = setup_directory_path()
    # Download contacts from Salesforce
    CONTACTS, ENROLMENTS = download_SF_contacts_data()
    # Download DfE establishments and trusts data
    ESTABLISHMENTS, TRUSTS = download_dfe_data(DIR_PATH)
    # Choose what reports to run
    OUTPUT_PREF = output_preferences()
    # Run reports
    run_reports(DIR_PATH, CONTACTS, ESTABLISHMENTS, TRUSTS, ENROLMENTS, OUTPUT_PREF)
    # Terminate program
    quit()
    

if __name__ == '__main__': # run program if running from .py file, else import as a module
    main()