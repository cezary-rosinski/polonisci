import requests
from tqdm import tqdm
import sys
sys.path.insert(1, 'C:/Users/Cezary/Documents/IBL-PAN-Python')
import pandas as pd
import json
from concurrent.futures import ThreadPoolExecutor
import regex as re

#%%def
# list_data = {}    
def get_names(url, discipline):
    global list_data
    
    response = requests.get(url)
    response2= response.json()['results']
    
    
    for resp in response2:
        usrname = resp['personalData']
        ident=resp['id']
        list_data[ident]=usrname
        #list_data.append(ident)
        
    try:
        token = response.json()['pagination']['token']
        
        get_names(f'https://radon.nauka.gov.pl/opendata/polon/employees?resultNumbers=100&disciplineName={discipline}&penaltyMarker=false&token={token}', discipline)
    except KeyError:
        pass
    return

# get_names('https://radon.nauka.gov.pl/opendata/polon/employees?resultNumbers=100&disciplineName=literaturoznawstwo&penaltyMarker=false')
#%%download all the people for all the disciplines

dyscypliny_df = pd.read_excel('pol-on_dyscypliny_zestawienie.xlsx')
dyscypliny_set = set(dyscypliny_df['Dyscypliny - Nazwa dyscypliny'].to_list())

dyscypliny_response = {}    
for dyscyplina in tqdm(dyscypliny_set):
    # dyscyplina = list(dyscypliny_set)[0]
    list_data = {}
    get_names(f'https://radon.nauka.gov.pl/opendata/polon/employees?resultNumbers=100&disciplineName={dyscyplina}&penaltyMarker=false', dyscyplina)
    dyscypliny_response.update({dyscyplina: list_data})
    
with open('dyscypliny_radon_response.json', 'w') as outfile:
    json.dump(dyscypliny_response, outfile, ensure_ascii=True)    

#%% download detailed info for each person
with open('dyscypliny_radon_response.json', 'r') as f:
    dyscypliny_response = json.load(f) 
    
people_ids = set([e for sub in {tuple(v.keys()) for k,v in dyscypliny_response.items()} for e in sub])
    
# person_id = list(people_ids)[0]

radon_response = {}

# for person_id in tqdm(people_ids):
def get_radon_info_for_person(person_id):
    url = 'https://radon.nauka.gov.pl/opendata/scientist/search'
    
    body={
      "resultNumbers": 1,
      "token": None,
      "body": {
        "uid": person_id,
        "firstName": None,
        "lastName": None,
        "employmentMarker": None,
        "employmentStatusMarker": None,
        "activePenaltyMarker": "No",
        "calculatedEduLevel": None,
        "academicDegreeMarker": None,
        "academicTitleMarker": None,
        "dataSources": None,
        "lastRefresh": None
      }}
    response=requests.post(url,  json=body).json()
    radon_response.update({person_id: response.get('results')})
    
    
radon_response = {}
with ThreadPoolExecutor() as executor:
    list(tqdm(executor.map(get_radon_info_for_person,people_ids), total=len(people_ids)))

with open('osoby_radon_response.json', 'w') as outfile:
    json.dump(radon_response, outfile, ensure_ascii=True)
    
#%% filter polish philologists
with open('osoby_radon_response.json', 'r') as f:
    radon_response = json.load(f) 

test = radon_response.get(list(radon_response.keys())[0])

ttt = {k:v for k,v in radon_response.items() if v[0].get('professionalTitles') and any(e.get('fieldName').strip() == 'filologia polska' for e in v[0].get('professionalTitles'))}

ok = {}
for k,v in tqdm(radon_response.items()):
    if v:
        for e in v:
            if e.get('professionalTitles'):
                for el in e.get('professionalTitles'):
                    # if el.get('fieldName') and el.get('fieldName').strip() == 'filologia polska' and el.get('professionalTitleName').strip() == 'Magister': #1 podejście
                    # if el.get('fieldName') and 'filologia polska' in el.get('fieldName').strip() and el.get('professionalTitleName').strip() == 'Magister': #2 podejście
                    if el.get('fieldName') and re.findall('filolog.+? polsk', el.get('fieldName')) and el.get('professionalTitleName').strip() == 'Magister': #3 podejście
                        ok.update({k:v})

#len(ok) --> 1527 vs. 1537
#dyscyplina polonistyka
polonisci_z_dyscyplina = list(dyscypliny_response.get('polonistyka').keys())
for pol in polonisci_z_dyscyplina:
    if pol not in ok:
        ok.update({pol:radon_response.get(pol)})
#len(ok) --> 1571 vs. 1581

#UWAGA --> 'filologia polska' != 'fieldName, ale 'filologia polska' in 'fieldName'

academic_degrees_disciplines = set()
for k,v in tqdm(radon_response.items()):
    if v:
        for e in v:
            if e.get('academicDegrees'):
                for el in e.get('academicDegrees'):
                    academic_degrees_disciplines.add(el.get('disciplineName'))
    
#Uwaga na puste zwrotki: 
{'92364B6FE6E86C988E5CB755617B6F94E8448393': [],
 '71CACA712302948FA6933A2DE5AA52D0CC99344C': [],
 'AF123CA4CA980C31074C826C2F99FFEE892FDED0': [],
 'CC453896E719532D8E7CAB0A250249F473A4AA56': [],
 '9D4739B172A329E59E3FB26D91F2780AAD12FD60': [],
 'E91AA2154BEB06E08E479F3511FE60C1CB51F42F': [],
 '9C26E10F233A47D334D06F1662CCB2B8FB9E53F8': [],
 'B792B1FB8B50B9E8E4B0D0CB0666F45368B3EA1D': [],
 'D6D25FA16A16D1AA0BA9C9C2140EC9C6270E1B1F': [],
 '36621D8B404ED6D7C2CC1BD6B9EA7E415B3B2F33': [],
 '248C7CEE2FCAF0CB8E6F93F7FE07753A9AF88063': [],
 '2CE51EE407A7F89BB79782E6D247DD45F7F080A4': [],
 '477379786DF9EC3D67DDD0D22C85BBB99EBD6468': [],
 '00BBD5C8BE459DBED9C2AAD84EA2532E004C32DB': [],
 '101A28BD1A7E497CB52A79DD7A3DE749FE2B8584': [],
 'DA0D7E477AA78A14472CCECB418E9E42ECA4B8C5': [],
 'CDFCC98EDB2CD2EBCDF03D71025A67D3F5DD4234': [],
 '5FB65836AF1F407502A95F1C62AF17CBF7FDA646': [],
 'D2963C1090EBB0D690F192A0C601AA89C98214BB': [],
 'F68D334A1C53FCCA0482FEA117C3A1C6E6892515': [],
 '2C9A9347D0B3160DBA0C3D72E95F0FAC1F246F12': [],
 '57CEB81F93B962853BA5FCDE405B41A78A3D068F': [],
 '53F9D300AA7B8D7EC1EA6670D1360CBFB0E6A9BD': [],
 '42DF1F8BE3326B72EADAB521015D899CBCEC3FEA': [],
 'BF32B882A78043D05E26551299C65D4FC5F5CCEB': [],
 '76EB14AB300CAE09AB5261E4C4104EB06BB1A166': [],
 '1B620BB6C9D79BC0653BD3A1562BB650A7F94633': [],
 'A19A1712594B82966BC8B801EB81BC8CDAB11338': [],
 'C8EFF6272752B82C0642F3B4AE97E36ECB9FE11B': [],
 'F635EC4B71F335B75BE1780FE37954261F335738': [],
 'DDE9A6F85D356D9C3295E54BB974879A3AC16279': [],
 '9B1E0311FEA166A2892C8C0449C6A74FCCC21896': [],
 'B907C77FA05AC384D7DCF1AD47BA4EC1F5445E31': [],
 'AE10A1580D552639B5322BED2E201210E2A6A855': [],
 'C7A02D4E8AE18ED10B02FCF00582F63474C71062': [],
 '3784CE479A156CBC1E14A6D4EE03F879424F3ECB': [],
 'E3C4441A72511BA3A7F139C401A705FD1F1F9935': [],
 '2493F7EA32D76126F8BAE622520F4B3FD454E6B4': [],
 '3B963F01CA16FCA7C904DAF376D6AD488EF1CB30': [],
 'A424A7EB5DBF07E1AAF2ED57D90C48B372EDEF85': [],
 '902BA0B2E96E4CDABEAE38D0175C22B2164F2717': [],
 '23C117EB182325102A0455985A6B0CD64A2CFAA3': [],
 'CBE207DFA160B5FDF6FD82B7B717986A12157AE6': [],
 '665C8E101503533DBC9D59ACC91EDA3E2565E30C': [],
 '7A0B3A61393CF71611F7010B1C95C5DC9F220440': [],
 'DFCC742A1ECAD489CAF5C0B888588C1EB25FFA8E': [],
 '332FE4D2C6076072F87D6255CB3293B6A39275E8': [],
 '9158487FFA8D73DD53F25746DD74841B1E8190D0': [],
 'D2389FF4210CBD0752B82D27F7F7E36F04BA592B': [],
 '617C4B9E24FC431F1F80F551AFE7F0DA8B040AD1': [],
 'F164D188B8B49FE88AFD17AC4C006F687038F008': [],
 'C6B97D4E68B018051E97D5AEF6BCE7248E82AD04': [],
 'AB0885DA0FFF3CA391E76CC721DF93055E6D4C28': [],
 '177B33924BC75D21D7F752BF3B2B1411EB7852B0': [],
 '94169216EF2646A7F6B15576C5D63362082FA3CC': [],
 '02C06BFAE2CE182FC68A44EE34F7F794FE0359B7': [],
 'DC9549245826C6F58347D3FD55D9EBB057EFE6AF': [],
 '9995285994BA78640CF2B6B89E5C7A81D1D9FD7A': [],
 'A7679266960833C9BEF8FFB151819AC70357F335': [],
 '5F554A94FF60A8D962C5C68659DEA88399ECDE90': [],
 '85957BA3A38BC1D2872B11EF3678BE118A572E07': [],
 '2D7B981726978DB4388A88970D561B1CDA3013BF': [],
 '23166ED5171C01F390586D26B3661BB2054D9106': [],
 'A8D6587863BE6DD4D701C4660EB1C9F4334806E7': []}

#%% notatki
first_name, last_name = 'Ewa Szczepan'.split(' ')
radon_response.get(''.join({tuple([ka for ka,va in v.items() if va.get('firstName') == first_name and va.get('lastName') == last_name]) for k,v in dyscypliny_response.items() if any(va.get('firstName') == first_name and va.get('lastName') == last_name for va in v.values())}))

{k:v for k,v in radon_response.items() if v and v[0].get('personalData').get('lastName') == last_name and v[0].get('personalData').get('firstName') == first_name}

{k:[e.get('institutionName') for e in v[0].get('employments')] for k,v in radon_response.items() if k in polonisci_z_dyscyplina}

#%%stare

#orcid

url = f'https://pub.orcid.org/v3.0_rc2/{orcid}'
            headers = {'Accept': 'application/json'}
            
            r=requests.get(url, headers=headers)
            
            
https://pub.orcid.org/v3.0/csv-search/?q=affiliation-org-name:ORCID&fl=orcid,given-names,family-name,current-institution-affiliation-name,past-institution-affiliation-name


url = 'https://pub.orcid.org/v3.0/expanded-search/?q=Tomasz%20Umerle'
url = 'https://pub.orcid.org/v3.0/expanded-search/?q=(family-name:Szymański AND given-names:Leszek Emil)'
headers = {'Accept': 'application/json'}
r=requests.get(url, headers=headers).json()




#radon
url = 'https://radon.nauka.gov.pl/opendata/scientist/search'

body={
  "resultNumbers": 1,
  "token": None,
  "body": {
    "uid": 'D10A6B73EC72024B6182C8410837944E7049FE5F'
,
    "firstName": None,
    "lastName": None,
    "employmentMarker": None,
    "employmentStatusMarker": None,
    "activePenaltyMarker": "No",
    "calculatedEduLevel": None,
    "academicDegreeMarker": None,
    "academicTitleMarker": None,
    "dataSources": None,
    "lastRefresh": None
  }}
response=requests.post(url,  json=body).json()
print(response.url)
response2= response.json()['results']
for result in response2:
    orcid_name.append(result['personalData'])
    
    
    
#polon
disciplin = 'językoznawstwo'
disciplin = 'literaturoznawstwo'
list_data = {}    
def get_names(url):
    global list_data
    
    response = requests.get(url)
    response2= response.json()['results']
    
    
    for resp in response2:
        usrname = resp['personalData']
        ident=resp['id']
        list_data[ident]=usrname
        #list_data.append(ident)
        
    try:
        token = response.json()['pagination']['token']
        
        get_names(f'https://radon.nauka.gov.pl/opendata/polon/employees?resultNumbers=100&disciplineName=literaturoznawstwo&penaltyMarker=false&token={token}')
    except KeyError:
        pass
    return

get_names('https://radon.nauka.gov.pl/opendata/polon/employees?resultNumbers=100&disciplineName=literaturoznawstwo&penaltyMarker=false')
    
    
#pomysł --> wyszukać zidentyfikowane instytucje w serwisie nauka-polska i tę listę wyposażyć w identyfikatory orcid i inne identyfikatory https://nauka-polska.pl/#/results?_k=d1k0vj
# co z polonem i radonem?
    
    
    
    
    
    
    