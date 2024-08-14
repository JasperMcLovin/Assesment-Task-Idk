import pandas as pd
import matplotlib.pyplot as plt
from sgp4.api import Satrec

df = pd.read_csv(
    'https://celestrak.org/NORAD/elements/gp.php?GROUP=active&FORMAT=2le',
    header=None,
    names=['Satellites']
)

s = str(df[0])
t = str(df[1])
satellite = Satrec.twoline2rv(s, t)

jd, fr = 2458826.5, 0.8625
e, r, v = satellite.sgp4(jd, fr)
e

print(r)
print(v)


