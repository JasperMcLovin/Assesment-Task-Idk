import pandas as pd
import matplotlib.pyplot as plt
import requests

df = pd.read_csv('https://celestrak.org/NORAD/elements/gp.php?GROUP=active&FORMAT=csv')
df = df.filter(['OBJECT_NAME', 'NORAD_CAT_ID'])
df['OBJECT_NAME'] = df['OBJECT_NAME'].str.lower()

def get_data():
    search = input('Search For Satellite: ')
    ID = df.at[search, 1]
    data = pd.read_csv(f'https://celestrak.org/NORAD/elements/gp.php?CATNR={ID}&FORMAT=CSV')
    print(data)

get_data()