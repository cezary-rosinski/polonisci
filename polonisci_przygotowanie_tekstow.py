import sys
sys.path.insert(1, 'C:/Users/Cezary/Documents/IBL-PAN-Python')
from my_functions import gsheet_to_df
from glob import glob
import regex as re

#%%

polonisci_db = gsheet_to_df('1Ilaek1uiYyPy4L5x5u4pWlBYOlZQPk1Q05Wcbv5E3jI', 'selekcja polonistów')

path = r"C:\Users\Cezary\Documents\polonisci\data\bibliotekanauki\txt\abstract_pl/"
abstract_files = [f for f in glob(f"{path}*", recursive=True)]

path = r"C:\Users\Cezary\Documents\polonisci\data\bibliotekanauki\txt\text_pl/"
text_files = [f for f in glob(f"{path}*", recursive=True)]