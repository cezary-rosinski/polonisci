from __future__ import unicode_literals
import requests
from bs4 import BeautifulSoup
import pandas as pd
import regex as re
import time
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import json
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from lxml import etree
import sys
sys.path.insert(1, 'C:/Users/Cezary/Documents/IBL-PAN-Python')
from my_functions import gsheet_to_df

#%% main
page_no = 1
url = f"https://biuletynpolonistyczny.pl/pl/people/?csrfmiddlewaretoken=gNmwp8C0klFn8RDbqnxZPQl6eo3WmDYB&person_first_name=&person_last_name=&person_disciplines=&person_institutions__institution_city__country=1&o=-person_date_add&per_page=90&page={page_no}"

r = requests.get(url).content
soup = BeautifulSoup(r, 'lxml')
dom = etree.HTML(str(soup))

max_page = int(dom.xpath("//a[@class = 'paginate__pages']")[0].text)

list_of_people = []
while page_no <= max_page:
    print(page_no)
    url = f"https://biuletynpolonistyczny.pl/pl/people/?csrfmiddlewaretoken=gNmwp8C0klFn8RDbqnxZPQl6eo3WmDYB&person_first_name=&person_last_name=&person_disciplines=&person_institutions__institution_city__country=1&o=-person_date_add&per_page=90&page={page_no}"
    r = requests.get(url).content
    soup = BeautifulSoup(r, 'lxml')
    result = [(t.text.strip(), l['href']) for t, l in zip(soup.select('b'), soup.select('.list__cols'))]
    list_of_people.extend(result)
    page_no += 1

df = pd.DataFrame(list_of_people, columns=['name', 'url'])
df.to_excel('polonisci_biuletyn_linki.xlsx', index=False)





#%% notatki
for li in dom.xpath("//a[@class = 'paginate__pages']"):
    print(li.text)
    
for li in dom.xpath("//li[@class = 'paginate__input']"):
    print(li.text)

[(t.text.strip(), l['href']) for t, l in zip(soup.select('b'), soup.select('.list__cols'))]
[(e.text, e['href']) for e in soup.select('.list__cols')]
[(e.text) for e in soup.select('.is-truncated')]


soup.find_all('.paginate__input')



dir(soup.find_all('b')[0])
str(soup)
soup.select('.list__cols--content')[0]
soup.select('a')[0]
a.list_item.list_item--col