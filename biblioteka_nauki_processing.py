import ijson
from tqdm import tqdm
from bs4 import BeautifulSoup
import sys
sys.path.insert(1, 'C:/Users/Cezary/Documents/IBL-PAN-Python')
from my_functions import gsheet_to_df
import pickle
import Levenshtein as lev
import pandas as pd
import requests
from concurrent.futures import ThreadPoolExecutor
import os
from glob import glob
import regex as re

#%%

##ograniczamy zbiór tylko do artykułów
##sprowadzić imiona i nazwiska w tabeli i w danych bibliotekinauki do alfabetu łacińskiego


list_of_people = set([e.lower() for e in gsheet_to_df('1TxqTCsnDmoEBihAT7NjW6Ghb-AJ2F5e1PQwk5F6sR9U', 'Sheet1')['lastName'].to_list() if e and isinstance(e, str)])
hyphen_people = set([el for sub in [e.split('-') for e in list_of_people if '-' in e] for el in sub])
list_of_people = list_of_people | hyphen_people

json_path = r"C:\Users\Cezary\Documents\polonisci\data\BibNauk_dump_2022_10_14.json"

ok_records = {}

with open(json_path, encoding='utf-8') as jotson:
    bibnau_full_dump = ijson.items(jotson, 'item')
    for obj in tqdm(bibnau_full_dump):
        soup = BeautifulSoup(obj, 'xml')
        record_id = soup.find('identifier').text
        discipline = soup.find_all('article-categories')
        try:
            discipline = [e.find('subject').text for e in discipline]
        except AttributeError:
            discipline = []
        t = soup.find_all('contrib')
        for contrib in t:
            if contrib.find('role').text == 'author' and contrib.find('surname').text.lower() in list_of_people:
                ok_records.update({record_id: {'discipline': discipline,
                                               'record': obj}})
        
   
disciplines = set([v.get('discipline')[0] for k,v in ok_records.items() if v.get('discipline')])

with open('data/bn_records.pickle', 'wb') as file:
    pickle.dump(ok_records, file)
#%%

people = gsheet_to_df('1TxqTCsnDmoEBihAT7NjW6Ghb-AJ2F5e1PQwk5F6sR9U', 'Sheet1')[['id', 'firstName', 'middleName', 'lastName']].set_index('id')
people = people.loc[people['lastName'].notnull()].to_dict(orient='index')
last_names = {}
for k,v in people.items():
    last_names.setdefault(v.get('lastName').lower(), []).append({'id': k, 'firstName': v.get('firstName').lower()})
    
last_names_hyphen = {}
for k,v in last_names.items():
    if '-' in k:
        k = k.split('-')
        for e in k:
            last_names_hyphen.setdefault(e.strip(), []).extend(v)

with open('data/bn_records.pickle', 'rb') as file:
    ok_records = pickle.load(file)

ok_records_ok_people = {}    
for k,v in tqdm(ok_records.items()):
    # k = 'oai:bibliotekanauki.pl:113793'
    # v = ok_records.get(k)
    if v.get('discipline') == ['Humanities']:
        soup = BeautifulSoup(v.get('record'), 'xml')
        languages = list(soup.find('article-title').attrs.values())
        if 'pl' in languages:
            p = soup.find_all('contrib')
            for e in p:
                # e = p[0]
                last_name = e.find('surname').text.lower()
                try:
                    first_name = e.find('given-names').text.lower()
                    person_matches = last_names.get(last_name)
                    if not person_matches:
                        person_matches = last_names_hyphen.get(last_name)
                    if person_matches:
                        for m in person_matches:
                            # m = person_matches[0]
                            ratio = lev.ratio(first_name, m.get('firstName'))
                            if ratio > 0.7:
                                ok_records_ok_people.update({k:{'discipline': v.get('discipline'),
                                                                'article_title': soup.find('article-title').text,
                                                                'person_from_article': f'{first_name} {last_name}',
                                                                'person_id': m.get('id'),
                                                                'ratio': ratio}})
                except AttributeError:
                    pass
                

  
# df = pd.DataFrame().from_dict(ok_records_ok_people, orient='index')
# df.to_excel('data/hity z biblitekinauki.xlsx')
        
wrong_records = gsheet_to_df('1TxqTCsnDmoEBihAT7NjW6Ghb-AJ2F5e1PQwk5F6sR9U', 'hity z bibliotekinauki')
wrong_records = wrong_records.loc[wrong_records['BŁĄD'] == 'True']['id tekstu'].to_list()
ok_records_ok_people = {k:v for k,v in ok_records_ok_people.items() if k not in wrong_records}

#harvesting pdfs
ok_records_prep = {k:v for k,v in ok_records.items() if k in ok_records_ok_people.keys()}

ok_records_to_harvest = {}
ok_records_to_harvest_abstracts = {}
for k,v in tqdm(ok_records_prep.items()):
    # k = 'oai:bibliotekanauki.pl:345026'
    # v = ok_records.get(k)
    soup = BeautifulSoup(v.get('record'), 'xml')
    if soup.find('article-title').attrs.get('xml:lang') == 'pl':
        ok_records_to_harvest.update({k:v})
    if soup.find('abstract'):
        if soup.find('abstract').attrs.get('xml:lang') == 'pl':
            ok_records_to_harvest_abstracts.update({k:v})
    

def harvest_bibliotekanauki(record):
    k, v = record
    soup = BeautifulSoup(v['record'], 'xml')
    uri = soup.find('self-uri')['xlink:href']
    with open(f"data/bibliotekanauki/{k.split(':')[-1]}.pdf", 'wb') as file:
        content = requests.get(uri, stream=True).content
        file.write(content)

with ThreadPoolExecutor() as executor:
    list(tqdm(executor.map(harvest_bibliotekanauki, ok_records_to_harvest.items()), total=len(ok_records_to_harvest)))
    
abstract_pdfs = [f"C:\\Users\\Cezary\\Documents\\polonisci\\data\\bibliotekanauki\\pdf\\abstract_pl\\{k.split(':')[-1]}.pdf" for k,v in ok_records_to_harvest_abstracts.items()]
abstract_hocrs = [f"C:\\Users\\Cezary\\Documents\\polonisci\\data\\bibliotekanauki\\hOCR\\abstract_pl\\{k.split(':')[-1]}.alto.hOCR" for k,v in ok_records_to_harvest_abstracts.items()]
path = r'C:\Users\Cezary\Documents\polonisci\data\bibliotekanauki\pdf\abstract_pl/'
path2 = r'C:\Users\Cezary\Documents\polonisci\data\bibliotekanauki\hOCR\abstract_pl/'
files_pdf_all = [f for f in glob(f"{path}*", recursive=True)]
files_hocr_all = [f for f in glob(f"{path2}*", recursive=True)]
[os.remove(e) for e in files_pdf_all if e not in abstract_pdfs]
[os.remove(e) for e in files_hocr_all if e not in abstract_hocrs]
# humanities = {k:v for k,v in ok_records.items() if 'Humanities' in v.get('discipline')}

#%% automatyczna segmentacja

#abstrakty
path = r'C:\Users\Cezary\Documents\polonisci\data\bibliotekanauki\hOCR\text_pl/'
files_hocr = [f for f in glob(f"{path}*", recursive=True)]

url = 'https://converter-hocr.services.clarin-pl.eu/convert/'

headers = {
    'accept': 'application/json',
    # requests won't add a boundary if this header is set when you pass files=
    # 'Content-Type': 'multipart/form-data',
}

params = {
    # 'class_name': 'normal',
    'html': 'false',
    'word_transfer': 'true',
}

def segment_hocr(file):
# for file in tqdm(files_hocr):
    # file = files_hocr[1]
    files = {
        # 'file': open('bibliotekanauki_87574.alto.hOCR', 'rb'),
        'file': open(file, 'rb')}
    file_name = re.findall('(\d+)(?=\.)', file)[0]

    response = requests.post(url, params=params, headers=headers, files=files)

    soup = BeautifulSoup(response.content, 'xml')
    try:
        results.update({file_name: {'abstract_pl': soup.find("div", {"class": "abstract"}).text.strip()}})
    except AttributeError:
        results.update({file_name: {'abstract_pl': None}})
        
    try:
        results[file_name].update({'text': '/n'.join([e.text.strip() for e in soup.find_all("div", {"class": "normal"})])})
    except AttributeError:
        results[file_name].update({'text': None})
        
results = {}
with ThreadPoolExecutor() as executor:
    list(tqdm(executor.map(segment_hocr,files_hocr), total=len(files_hocr)))

with open('data/bn_records_po_segmentacji.pickle', 'wb') as file:
    pickle.dump(results, file)

!!!tutaj

test = '/n'.join([e.text.strip() for e in results.get(list(results.keys())[0]).get('text')])

results.get(list(results.keys())[0]).get('abstract_pl')

abstrakty = {k:v.get('abstract_pl') for k,v in results.items()}
# test = set([v.split(' ')[0] for k,v in abstrakty.items() if v])

# ['Abstrakt:', 'ABSTRAKT', 'Abstrakt', 'Abstrakt.', 'STRESZCZENIE', 'Streszczenie', 'Streszczenie.', 'Streszczenie:']

abstrakty = {k:re.sub('^Abstrakt\:|^ABSTRAKT|^Abstrakt\.|^Abstrakt|^STRESZCZENIE|^Streszczenie\:|^Streszczenie\.|^Streszczenie', '', v).strip().lstrip('.').lstrip(':').lstrip('|').strip() if v else v for k,v in abstrakty.items()}

path = r'C:\Users\Cezary\Downloads\clarin_bibliotekanauki_hOCR\abstrakty/'

for k,v in abstrakty.items():
    if v:
        with open(f"{path}{k}.txt", 'wt', encoding='utf-8') as f:
            f.write(v)


#pełne teksty
        
#%%
s = BeautifulSoup(ok_records[1], 'xml')

s.find('identifier').text

s = s.find_all('article-categories')
[e.find('subject').text for e in s]

ttt = '''<record xmlns="http://www.openarchives.org/OAI/2.0/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
	<header>
		<identifier>oai:bibliotekanauki.pl:213208</identifier>
		<datestamp>2022-04-05T23:24:30.158Z</datestamp>
		<setSpec>247</setSpec>
	</header>
	<metadata>
		<article xmlns="http://jats.nlm.nih.gov" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://jats.nlm.nih.gov https://jats.nlm.nih.gov/archiving/1.2/xsd/JATS-archivearticle1.xsd" article-type="research-article">
			<front>
				<journal-meta>
					<journal-title-group>
						<journal-title>Prace Instytutu Lotnictwa</journal-title>
					</journal-title-group>
					<issn pub-type="ppub">0509-6669</issn>
					<issn pub-type="epub">2300-5408</issn>
					<publisher>
						<publisher-name>Sieć Badawcza Łukasiewicz - Instytut Lotnictwa</publisher-name>
					</publisher>
				</journal-meta>
				<article-meta>
					<article-categories>
						<subj-group>
							<subject>Engineering and technical sciences</subject>
							<subj-group>
								<subject>civil engineering and transport</subject>
							</subj-group>
						</subj-group>
					</article-categories>
					<title-group>
						<article-title xml:lang="pl">Zarządzanie kryzysem przy użyciu mediów społecznościowych</article-title>
						<trans-title-group xml:lang="en">
							<trans-title>Crisis management via social media</trans-title>
						</trans-title-group>
					</title-group>
					<contrib-group>
						<contrib>
							<name name-style="western">
								<surname>Chwiałkowska</surname>
								<given-names>A.</given-names>
							</name>
							<role>author</role>
							<xref ref-type="aff" rid="aff-213208-0"/>
						</contrib>
					</contrib-group>
					<aff id="aff-213208-0">
						<institution content-type="orgname">Uniwersytet Mikołaja Kopernika w Toruniu, Wydział Nauk Ekonomicznych i Zarządzania</institution>
					</aff>
					<pub-date date-type="pub">
						<year>2012</year>
					</pub-date>
					<pub-date date-type="published">
						<year>2012</year>
					</pub-date>
					<pub-date date-type="collection">
						<year>2012</year>
					</pub-date>
					<abstract xml:lang="pl">
						<p>Popularyzacja mediów społecznościowych daje przedsiębiorstwom wiele możliwości nawiązania dialogu i interakcji z konsumentami, lepszego zrozumienia ich potrzeb, a także zbudowania z nimi trwałych relacji oraz utrzymywania wokół marki całej społeczności fanów. Dzięki nim, treści mogą rozprzestrzeniać się z niespotykaną dotąd szybkością, przyjmując tak zwany wirusowy charakter. Zmienia się również sam konsument, który oczekuje teraz natychmiastowej odpowiedzi na wszelkie swoje pytania i wątpliwości oraz coraz częściej przedstawia swoje żale i skargi dotyczące przedsiębiorstwa w mediasferze internetowej. Wszystkie te czynniki sprawiają, że współczesna organizacja staje przed nowymi wyzwaniami, do przezwyciężenia których przedsiębiorstwo musi się w odpowiedni sposób przygotować. Od czasu głośnej sprawy dotyczącej skażonego cyjankiem Tylenolu w 1982 roku wiele się zmieniło, zwłaszcza, że rozwinęła się gospodarka internetowa. W tej nowej rzeczywistości zarządzanie kryzysem, zwłaszcza w sferze PR, przyjmuje nowy wymiar. W dobie Internetu i mediów społecznościowych, wiadomości w postaci tekstu, obrazu bądź video rozchodzą się lotem błyskawicy i w krótkim okresie czasu docierają do ludzi z różnych części globu. Dzięki nowoczesnym technologiom kryzys wybucha w przerażająco szybkim tempie, wystarczy jedna niekorzystna informacja (która może być ujawniona przez kogokolwiek) na temat naszego przedsiębiorstwa, aby utworzyła się wokół niej cała społeczność rozzłoszczonych klientów. Ponadto, w wirtualnej rzeczywistości niezwykle trudno jest zataić informacje bądź usunąć te kompromitujące, co stwarza jeszcze większe wyzwanie dla specjalistów w dziedzinie PR. Celem artykułu jest zatem przedstawienie przykładów tego, jak przedsiębiorstwa radzą sobie z kryzysem wykorzystując do tego celu obecność w mediach społecznościowych. Opisane zostały ponadto przykłady przedsiębiorstw, które nie wykorzystały potencjału tkwiącego w platformach społecznościowych i zignorowały siłę oddziaływania wirtualnych społeczności. Pozwoli to na stworzenie na tej podstawie swoistego kodeksu dobrych praktyk dla zarządzania kryzysem z wykorzystaniem mediów społecznościowych.</p>
					</abstract>
					<trans-abstract xml:lang="en">
						<p>Increasing popularity of social media gives businesses a wide spectrum of possibilities to enter into díalos and interaction with consumers, to better understand their needs, to build durable relations with clients and to maintain brand communities. Thanks to social media, content may be transmitted with an unprecedented speed in the so-called viral manner. The consumer has been undergoing change too, expecting now instant answers to all his questions and doubts and more often than ever expressing complaints about a company in the media sphere of the internet. All these factors combine to cause organizations to face new challenges, the overcoming of which requires an appropriate preparation. The goal of this paper is to present some examples of organizations dealing with crises with the use of social media. Additionally, the paper describes some organizations which failed to tap into the potentialities offered by social networking services and ignored the power of virtual communities. This approach will allow formulating a code of good practices regarding crisis management through social networks so that organizations could be adequately prepared to respond to crisis in a way that not only helps them to avoid failure but will actually strengthen their image.</p>
					</trans-abstract>
					<issue>4 (225)</issue>
					<issue-id>12034</issue-id>
					<fpage>265</fpage>
					<lpage>279</lpage>
					<kwd-group xml:lang="pl">
						<kwd>zarządzanie kryzysem</kwd>
						<kwd>media społecznościowe</kwd>
						<kwd>raport Adwatch</kwd>
					</kwd-group>
					<kwd-group xml:lang="en">
						<kwd>crisis management</kwd>
						<kwd>social media</kwd>
						<kwd>Adwatch report</kwd>
					</kwd-group>
					<self-uri xlink:href="https://bibliotekanauki.pl/articles/213208.pdf" content-type="application/pdf"/>
				</article-meta>
			</front>
			<back>
				<ref-list>
					<ref id="ref-213208-0">
						<mixed-citation>1. Baer J., Nashid A., The Now Revolution. 7 shifts to make your business faster, smarter and more social, Wiley 2011.</mixed-citation>
					</ref>
					<ref id="ref-213208-1">
						<mixed-citation>2. Coombs T. W., Ongoing crisis communication - planning, managing and responding, Sage Publications, London 2007.</mixed-citation>
					</ref>
					<ref id="ref-213208-2">
						<mixed-citation>3. Li C, Bernoff J., Marketing technologu społecznych. Groundswell czyli jak wykorzystać Web 2.0 w twojej firmie, MT Business Ltd, 2008.</mixed-citation>
					</ref>
					<ref id="ref-213208-3">
						<mixed-citation>4. Mac A., E-przyjaciele. Zobacz co media społecznościowe mogą zrobić dla Twojej Firmy, One Press, Gliwice 2011.</mixed-citation>
					</ref>
					<ref id="ref-213208-4">
						<mixed-citation>5. Meerman D., Marketing i PR w czasie rzeczywistym, Jak błyskawicznie dotrzeć do rynku i nawiązać kontakt z klientem. Oficyna a Wolters Kluwer business, Warszawa 2011.</mixed-citation>
					</ref>
					<ref id="ref-213208-5">
						<mixed-citation>6. Niżnik W., SawickiT., Krzosek M., Kryzysy w social media, raport opublikowanego w ramach projektu AdWatch.pl realizowanego przy współpracy IRCenter Sp. zo.o. i Solnteractive SA, 2011.</mixed-citation>
					</ref>
					<ref id="ref-213208-6">
						<mixed-citation>7. Smith D., Beyond contingency planning: towards a model of crisis management, Organization Environment, Sage Publishing, 1990.</mixed-citation>
					</ref>
					<ref id="ref-213208-7">
						<mixed-citation>Strony internetowe:</mixed-citation>
					</ref>
					<ref id="ref-213208-8">
						<mixed-citation>-  Profil Frisco na Facebooku: https://www.facebook.com/pages/FRISCOPL/141767962518913, Fanpage Allegro na Facebooku: https://www.facebook.com/allegro,</mixed-citation>
					</ref>
					<ref id="ref-213208-9">
						<mixed-citation>- Fanpage Allegro na Facebooku: https://www.facebook.com/allegro</mixed-citation>
					</ref>
					<ref id="ref-213208-10">
						<mixed-citation>- Korporacyjny Profil BP na facebooku: https://www.facebook.com/BPAmerica?sk=wall,</mixed-citation>
					</ref>
					<ref id="ref-213208-11">
						<mixed-citation>- Dział PR firmy BP na Twitterze: https://twitter.com/BPGlobalPR,</mixed-citation>
					</ref>
					<ref id="ref-213208-12">
						<mixed-citation>- Grupa na Facebooku utworzona w ramach sprzeciwu wobec poczynań firmy Adidas: https://www.facebook.com/pages/adisucks/134728066598497,</mixed-citation>
					</ref>
					<ref id="ref-213208-13">
						<mixed-citation>- Korporacyjna strona Orange na Facebooku: https://www.facebook.com/orangepolska,</mixed-citation>
					</ref>
					<ref id="ref-213208-14">
						<mixed-citation>- Film bedącyczęściąkampanii Motrin: http://www.youtube.com/watch?v=X06SlTUBA38(11.09.2012),</mixed-citation>
					</ref>
					<ref id="ref-213208-15">
						<mixed-citation>- Konto Comcast na Twitterze: https://twitter.com/comcastcares,</mixed-citation>
					</ref>
					<ref id="ref-213208-16">
						<mixed-citation>- Film, który pojawił się na ten temat na YouTube: http://www.youtube.com/watch?v=su0U37w2tws (10.09.2012),</mixed-citation>
					</ref>
					<ref id="ref-213208-17">
						<mixed-citation>- New York Times, http://www.nytimes.eom/2004/09/l 7/nyregion/l7lock.html?_r=1 (19.09.2012),  Longley S., Columbia Spectator, http://www.columbiaspectator.com/2004/10/18/felled-bic-pens-and-law-suits-kryptonite-isnt-so-mighty-after-all (30.09.2012),</mixed-citation>
					</ref>
					<ref id="ref-213208-18">
						<mixed-citation>- Longley S., Columbia Spectator, http://www.columbiaspectator.com/2004/10/18/felled-bic-pens-and-law-suits-kryptonite-isnt-so-mighty-after-all (30.09.2012),</mixed-citation>
					</ref>
					<ref id="ref-213208-19">
						<mixed-citation>- Video obrazujące śpiącego pracownika Comcast, http://www.youtube.com/watch?v=CvVp7b5gzqU, (20.09.2012),</mixed-citation>
					</ref>
					<ref id="ref-213208-20">
						<mixed-citation>- Wypowiedź Patricka Doyle: http://www.youtube.com/watch?v=WXZUXn8RJeA, (16.09.2012).</mixed-citation>
					</ref>
				</ref-list>
			</back>
		</article>
	</metadata>
</record>'''


soup = BeautifulSoup(ttt, 'xml')
test = soup.find("contrib", {"role": "author"})

soup.find_all('contrib', {'role': 'author'})
soup.find('contrib')
dir(soup.find('contrib'))
t = soup.find('contrib')
t.find('role').text == 'author'









