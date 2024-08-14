import pandas as pd
import matplotlib.pyplot as plt
from sgp4 import omm
from sgp4.api import Satrec

# df = pd.read_csv('https://celestrak.org/NORAD/elements/gp.php?GROUP=active&FORMAT=xml')

with open('data.xml') as f:
   fields = next(omm.parse_xml(f))
sat = Satrec()
omm.initialize(sat, fields)

