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
t = ts.now()

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
    satellites = load.tle_file('https://celestrak.org/NORAD/elements/gp.php?GROUP=active&FORMAT=tle', reload=True)

bluffton = wgs84.latlon(+40.8939, -83.8917)
t0 = t
t1 = t + 1
t, events = satellite.find_events(bluffton, t0, t1, altitude_degrees=30.0)
event_names = 'rise above 30°', 'culminate', 'set below 30°'

eph = load('de421.bsp')
sunlit = satellite.at(t, t1).is_sunlit(eph)

for ti, event, sunlit_flag in zip(t, events, sunlit):
    name = event_names[event]
    state = ('in shadow', 'in sunlight')[sunlit_flag]
    print('{:22} {:15} {}'.format(
        ti.utc_strftime('%Y %b %d %H:%M:%S'), name, state,
    ))