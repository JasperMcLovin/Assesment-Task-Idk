import pandas as pd
import matplotlib.pyplot as plt
from skyfield.api import load
import csv
from skyfield.api import EarthSatellite, load
from datetime import datetime
from pytz import timezone

ts = load.timescale()

eastern = timezone('US/Eastern')

d = datetime(2024, 8, 14, 19, 27, 24)
e = eastern.localize(d)
t = ts.from_datetime(e)
dt = t.astimezone_and_leap_second('Australia/NSW')
print(dt)

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
t = ts.utc(dt)

days = t - satellite.epoch
print('{:.3f} days away from epoch'.format(days))

if abs(days) > 14:
    satellites = load.tle_file('https://celestrak.org/NORAD/elements/gp.php?GROUP=active&FORMAT=tle', reload=True)