import pandas as pd
import matplotlib.pyplot as plt
from skyfield.api import load
import csv
from skyfield.api import EarthSatellite, load
import datetime
from datetime import datetime
import pytz
from pytz import timezone
from skyfield.api import wgs84

ts = load.timescale()

australian = timezone('Australia/NSW')

d = datetime(2024, 8, 15, 11, 5, 56)
e = australian.localize(d)
t = ts.from_datetime(e)
print(t)

max_days = 7.0
name = 'satellites.csv'

base = 'https://celestrak.org/NORAD/elements/gp.php'
url = base + '?GROUP=active&FORMAT=csv'

if not load.exists(name) or load.days_old(name) >= max_days:
    load.download(url, filename=name)

with load.open('satellites.csv', mode='r') as f:
    data = list(csv.DictReader(f))

sats = [EarthSatellite.from_omm(ts, fields) for fields in data]
print('Loaded', len(sats), 'satellites')

by_name = {sat.name: sat for sat in sats}
satellite = by_name['ISS (ZARYA)']
print(satellite)

print(satellite.epoch.utc_jpl())

days = t - satellite.epoch
print('{:.3f} days away from epoch'.format(days))

if abs(days) > 14:
    satellites = load.tle_file(stations_url, reload=True)