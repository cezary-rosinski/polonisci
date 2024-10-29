import sys
sys.path.insert(1, 'C:/Users/Cezary/Documents/IBL-PAN-Python')
from my_functions import gsheet_to_df
from glob import glob
import regex as re
from tqdm import tqdm
import pickle
import pandas as pd
from bs4 import BeautifulSoup
import requests
from concurrent.futures import ThreadPoolExecutor
from sickle import Sickle

#%% przygotowanie PDF dla PH
polonisci_db = gsheet_to_df('1Ilaek1uiYyPy4L5x5u4pWlBYOlZQPk1Q05Wcbv5E3jI', 'selekcja polonistów')
polonisci_db2 = gsheet_to_df('1Ilaek1uiYyPy4L5x5u4pWlBYOlZQPk1Q05Wcbv5E3jI', 'selekcja polonistów 2024')

polonisci_db = pd.concat([polonisci_db, polonisci_db2])

polonisci_db_selected = polonisci_db.loc[(polonisci_db['is_polish_scientist'] == 'tak') &
                                         (~polonisci_db['author_id'].str.contains(',', na=False))]

text_ids = [e for e in polonisci_db_selected['id'].to_list()]

#%%
with open('data/bn_selected_records.pickle', 'rb') as file:
    selected_records = pickle.load(file)

selected_records = {k:v for k,v in selected_records.items() if k in text_ids}

# missing_oai = [e for e in text_ids if e not in selected_records.keys()]

#%% re-harvest for missing

# url = 'https://bibliotekanauki.pl/api/oai/articles'

# articles = []

# for record in tqdm(missing_oai):
#     sickle = Sickle(url)
#     record_oai = sickle.GetRecord(identifier=record, metadataPrefix='jats')
#     articles.append(record_oai.raw)

# for article in tqdm(articles):
    
#     soup = BeautifulSoup(article, 'xml')
#     record_id = soup.find('identifier').text
#     discipline = soup.find_all('article-categories')
#     try:
#         discipline = [e.find('subject').text for e in discipline]
#     except AttributeError:
#         discipline = []
#     selected_records.update({record_id: {'discipline': discipline,
#                                          'record': article}})

#%% harvesting PDFs


def harvest_bibliotekanauki(record):
    k, v = record
    soup = BeautifulSoup(v['record'], 'xml')
    uri = soup.find('self-uri')['xlink:href']
    with open(f"data/bibliotekanauki/pdf/{k.split(':')[-1]}.pdf", 'wb') as file:
        content = requests.get(uri, stream=True).content
        file.write(content)

with ThreadPoolExecutor() as executor:
    list(tqdm(executor.map(harvest_bibliotekanauki, selected_records.items()), total=len(selected_records)))





#%% stare rozwiązanie CLARIN

polonisci_db = gsheet_to_df('1Ilaek1uiYyPy4L5x5u4pWlBYOlZQPk1Q05Wcbv5E3jI', 'selekcja polonistów')
polonisci_db2 = gsheet_to_df('1Ilaek1uiYyPy4L5x5u4pWlBYOlZQPk1Q05Wcbv5E3jI', 'selekcja polonistów 2024')

polonisci_db = pd.concat([polonisci_db, polonisci_db2])

path = r"C:\Users\Cezary\Documents\polonisci\data\bibliotekanauki\txt\abstract_pl/"
abstract_files = [f for f in glob(f"{path}*", recursive=True)]

path = r"C:\Users\Cezary\Documents\polonisci\data\bibliotekanauki\txt\text_pl/"
text_files = [f for f in glob(f"{path}*", recursive=True)]

polonisci_db = polonisci_db.loc[polonisci_db['is_polish_scientist'] == 'tak']
text_ids = [e.split(':')[-1] for e in polonisci_db['id'].to_list()]

abstract_files_ok = [e for e in abstract_files if e.split('\\')[-1].replace('.txt', '') in text_ids]
text_files_ok = [e for e in text_files if e.split('\\')[-1].replace('.txt', '') in text_ids]

text_files_content = {}
for abstract in tqdm(abstract_files_ok):
    with open(abstract, encoding='utf-8') as f:
        x = f.read()
        text_files_content.update({abstract.split('\\')[-1].replace('.txt', ''): {'abstract': x}})
        
for text in tqdm(text_files_ok):
    with open(text, encoding='utf-8') as f:
        x = f.read()
        text_id = text.split('\\')[-1].replace('.txt', '')
        if text_id in text_files_content:
            text_files_content[text_id].update({'full text': x})
        else: text_files_content.update({text_id: {'full text': x}})
        
with open('data/polonisci_text_abstract.pickle', 'wb') as handle:
    pickle.dump(text_files_content, handle, protocol=pickle.HIGHEST_PROTOCOL)
    
# with open('filename.pickle', 'rb') as handle:
#     b = pickle.load(handle)