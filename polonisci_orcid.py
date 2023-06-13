import requests
from tqdm import tqdm
import sys
sys.path.insert(1, 'C:/Users/Cezary/Documents/IBL-PAN-Python')



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
        
        get_names(f'https://radon.nauka.gov.pl/opendata/polon/employees?resultNumbers=100&disciplineName=językoznawstwo&penaltyMarker=false&token={token}')
    except KeyError:
        pass
    return

get_names('https://radon.nauka.gov.pl/opendata/polon/employees?resultNumbers=100&disciplineName=językoznawstwo&penaltyMarker=false')
    
    
#pomysł --> wyszukać zidentyfikowane instytucje w serwisie nauka-polska i tę listę wyposażyć w identyfikatory orcid i inne identyfikatory https://nauka-polska.pl/#/results?_k=d1k0vj
# co z polonem i radonem?
    
    
    
    
    
    
    