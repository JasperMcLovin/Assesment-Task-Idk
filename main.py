import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv(
    'https://celestrak.org/NORAD/elements/gp.php?GROUP=active&FORMAT=tle',
    header=None,
    names=['Satellites']
)
print(df)



# def get_data():
    # search = input('Search For Satellite: ')
    # ID = df[df['OBJECT_NAME'] == f'{search}']['NORAD_CAT_ID'].values[0]
    # data = pd.read_csv(f'https://celestrak.org/NORAD/elements/gp.php?CATNR={ID}&FORMAT=tle')
    # print(data)

# get_data()