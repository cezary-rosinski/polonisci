import sys
sys.path.insert(1, 'C:/Users/Cezary/Documents/IBL-PAN-Python')
from my_functions import gsheet_to_df
from glob import glob
import regex as re
from tqdm import tqdm
import pickle

#%%

polonisci_db = gsheet_to_df('1Ilaek1uiYyPy4L5x5u4pWlBYOlZQPk1Q05Wcbv5E3jI', 'selekcja polonistów')

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