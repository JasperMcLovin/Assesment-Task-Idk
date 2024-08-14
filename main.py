import pandas as pd
import matplotlib.pyplot as plt
from sgp4 import omm
from sgp4.api import Satrec
import requests

link = 'https://celestrak.org/NORAD/elements/gp.php?GROUP=active&FORMAT=xml'
f = requests.get(link)
print(f.text)

# df = pd.read_csv('https://celestrak.org/NORAD/elements/gp.php?GROUP=active&FORMAT=xml')

#with open(f'{f}') as f:
 #   fields = next(omm.parse_xml(f))
#sat = Satrec()
#omm.initialize(sat, fields)

