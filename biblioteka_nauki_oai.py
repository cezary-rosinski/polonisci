# Repozytorium artykułów: https://bibliotekanauki.pl/api/oai/articles
# Repozytorium książek: https://bibliotekanauki.pl/api/oai/books
# Repozytorium rozdziałów prac zbiorowych: https://bibliotekanauki.pl/api/oai/chapters

import os
from sickle import Sickle
from tqdm import tqdm
from lxml.etree import parse, tostring, fromstring
import pandas as pd
import json

#%%

oai_urls = {
    'articles': 'https://bibliotekanauki.pl/api/oai/articles',
    'books': 'https://bibliotekanauki.pl/api/oai/books',
    'chapters': 'https://bibliotekanauki.pl/api/oai/chapters'
    }

articles = []
books = []
chapters = []
counter = 0
for key, url in oai_urls.items():
    if key in ['chapters', 'books']:
        sickle = Sickle(url)
        records = sickle.ListRecords(metadataPrefix='bits')
    else:
        sickle = Sickle(url)
        records = sickle.ListRecords(metadataPrefix='jats')
        
        for record in tqdm(records):
            if key == 'articles':
                articles.append(record.raw)
            elif key == 'books':
                books.append(record.raw)
            elif key == 'chapters':
                chapters.append(record.raw)
    counter += 1
    print(counter)

#"C:\Users\Nikodem\Desktop\ibl_workspace\projects\biblioteka_nauki\xmls\articles"

for i, record in tqdm(enumerate(articles)):
    with open(r"C:\Users\Nikodem\Desktop\ibl_workspace\projects\biblioteka_nauki\xmls\articles_jats\rec{}.xml".format(i), 'w', encoding='utf-8') as xml:
        xml.writelines(record)
        
for i, record in tqdm(enumerate(books)):
    with open(r"C:\Users\Nikodem\Desktop\ibl_workspace\projects\biblioteka_nauki\xmls\books_bits\rec{}.xml".format(i), 'w', encoding='utf-8') as xml:
        xml.writelines(record)
        
for i, record in tqdm(enumerate(chapters)):
    with open(r"C:\Users\Nikodem\Desktop\ibl_workspace\projects\biblioteka_nauki\xmls\chapters_bits\rec{}.xml".format(i), 'w', encoding='utf-8') as xml:
        xml.writelines(record)
        
        
#%%
disciplines = ['Agricultural sciences',
'Medical and health sciences',
'Social sciences',
'Engineering and technical sciences',
'Exact and natural sciences',
'Earth and the environment sciences',
'Humanities',
'Theological sciences',
'Art']

ssh_disciplines = ['Social sciences',
'Humanities',
'Art']


bib_nauk_subejcts = ['Social sciences',
'Humanities',
'Art']

ssh_identifiers = {
    'https://bibliotekanauki.pl/api/oai/articles': [],
    'https://bibliotekanauki.pl/api/oai/books': [],
    'https://bibliotekanauki.pl/api/oai/chapters': []}
dir_paths = [r"C:\Users\Nikodem\Desktop\ibl_workspace\projects\biblioteka_nauki\xmls\articles_jats",r"C:\Users\Nikodem\Desktop\ibl_workspace\projects\biblioteka_nauki\xmls\books_bits",r"C:\Users\Nikodem\Desktop\ibl_workspace\projects\biblioteka_nauki\xmls\chapters_bits"]
for path in dir_paths:  
    for filename in tqdm(os.listdir(path)):
       file_path = path + '\\' + filename
       tree = parse(file_path)
       subjects = tree.xpath('//*[local-name()="subject"]')
       subjects = [subject.text for subject in subjects if subject.text[0].isupper()]
       identifier = tree.xpath('//*[local-name()="identifier"]')
       if any([subject in ssh_disciplines for subject in subjects]):
           if 'articles' in path:
               ssh_identifiers['https://bibliotekanauki.pl/api/oai/articles'].append(identifier[0].text)
           elif 'books' in path:
               ssh_identifiers['https://bibliotekanauki.pl/api/oai/books'].append(identifier[0].text)
           else:
               ssh_identifiers['https://bibliotekanauki.pl/api/oai/chapters'].append(identifier[0].text)
       # ran = range(len(subjects) // 2)
       # for i in ran:
       #     item = []
       #     for i in range(2):
       #         item.append(subjects.pop().text)
       #     if item not in bib_nauk_subejcts: bib_nauk_subejcts.append(item)
          
#%%

with open(r"C:\Users\Nikodem\Desktop\ibl_workspace\projects\biblioteka_nauki\bibliotekanauki_ssh_identifiers.json", 'w') as jfile:
    json.dump(ssh_identifiers, jfile, ensure_ascii=False, indent=4)

