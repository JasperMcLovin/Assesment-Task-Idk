import pandas as pd
import matplotlib.pyplot as plt
import csv
from skyfield.api import *
from datetime import *
from pytz import *
import tkinter as tk
from tkinter import *
from tkinter import ttk
import json
from urllib.request import *
from matplotlib.dates import HourLocator, DateFormatter
import numpy as np
import math

ts = load.timescale()
t = ts.now()
max_days = 1.0
names = []
name = 'satellites.csv'
base = 'https://celestrak.org/NORAD/elements/gp.php'
url = base + '?GROUP=active&FORMAT=csv'
if not load.exists(name) or load.days_old(name) >= max_days:
    load.download(url, filename=name)
with load.open('satellites.csv', mode='r') as f:
    data = list(csv.DictReader(f))
    for row in data:
        names.append(row['OBJECT_NAME'])
sats = [EarthSatellite.from_omm(ts, fields) for fields in data]
names.sort()
def location_lookup():
  try:
    return json.load(urlopen('http://ipinfo.io/json'))
  except:
    return {"loc": "0, 0"}
location = location_lookup()
place = str(location['loc'])
comma = place.index(',')
lat = float(place.split(',')[0])
lon = float(place.split(',')[1])
bluffton = wgs84.latlon(lat, lon)
t0 = t
t1 = t+1
earth_radius_km = 6371.0

root = Tk()
root.title('The Worst Program Ever')
root.geometry("500x500")

def update(data):
	my_list.delete(0, END)

	for item in data:
		my_list.insert(END, item)

def fillout(e):
	my_entry.delete(0, END)

	my_entry.insert(0, my_list.get(ANCHOR))
	global selected
	selected = my_list.get(ANCHOR)

def check(e):
	typed = my_entry.get()

	if typed == '':
		data = names
	else:
		data = []
		for item in names:
			if typed.lower() in item.lower():
				data.append(item)

	update(data)				

my_label = Label(root, text="Search For A Satellite",
	font=("Helvetica", 14), fg="grey")

my_label.pack(pady=20)

my_entry = Entry(root, font=("Helvetica", 20))
my_entry.pack()

my_list = Listbox(root, width=50)
my_list.pack(pady=40)

update(names)

my_list.bind("<<ListboxSelect>>", fillout)

my_entry.bind("<KeyRelease>", check)

def get_info():
	new_win = Toplevel(root)
	new_win.title('Satellite Data')
	new_win.geometry('400x400')
	Label(new_win, text=f"Data For {selected}",font=("Helvetica", 20)).pack(pady=20)
	my_list = Listbox(new_win, width=70)
	my_list.pack(pady=30)
	
	t = ts.now()
	by_name = {sat.name: sat for sat in sats}
	satellite = by_name[f'{selected}']
	tf = ts.tt_jd(np.arange(satellite.epoch.tt - 1.0, satellite.epoch.tt + 1.0, 0.005))
	days = t - satellite.epoch
	if days > 0:
		time_epoch = '{:.3f} days past epoch'.format(days)
	else:
		time_epoch = '{:.3f} days until epoch'.format(abs(days))
	geocentric = satellite.at(t)
	lat, lon = wgs84.latlon_of(geocentric)
	v = geocentric.velocity.km_per_s
	speed = math.sqrt(pow(v[0], 2)+pow(v[1], 2)+pow(v[2], 2))

	my_list.insert(END, time_epoch)
	my_list.insert(END, f'Current Speed: {round(speed, 3)}km/s')
	my_list.insert(END, f'Current Latitude: {lat}')
	my_list.insert(END, f'Current Longitude: {lon}')
	my_list.insert(END, f'How many times {selected} will be over 30° in the next day:')

	t = ts.now()
	t, events = satellite.find_events(bluffton, t0, t1, altitude_degrees=30.0)
	event_names = 'rise above 30°', 'culminate', 'set below 30°'
	for ti, event in zip(t, events):
		name = event_names[event]
		ti.utc_strftime('%Y %b %d %H:%M:%S'), name
	eph = load('de421.bsp')
	sunlit = satellite.at(t).is_sunlit(eph)
	for ti, event, sunlit_flag in zip(t, events, sunlit):
		name = event_names[event]
		state = ('in shadow', 'in sunlight')[sunlit_flag]
		my_list.insert(END, '{:22} {:15} {}'.format(
        	ti.utc_strftime('%Y %b %d %H:%M:%S'), name, state,
    ))
		
	t = ts.now()
	difference = satellite - bluffton
	topocentric = difference.at(t)
	alt, az, distance = topocentric.altaz()

	my_list.insert(END, f'Where {selected} is in the sky:')

	if alt.degrees > 0:
		my_list.insert(END, f'{selected} is above the horizon')
	else:
		my_list.insert(END, f'{selected} is below the horizon')

	my_list.insert(END, f'Altitude: {alt}')
	my_list.insert(END, f'Azimuth: {az}')
	my_list.insert(END, 'Distance: {:.1f} km'.format(distance.km))

	fig, ax = plt.subplots()
	def label_dates_and_hours(axes):
		axes.xaxis.set_major_locator(HourLocator([0]))
		axes.xaxis.set_minor_locator(HourLocator([0, 6, 12, 18]))
		axes.xaxis.set_major_formatter(DateFormatter('0h\n%Y %b %d\n%A'))
		axes.xaxis.set_minor_formatter(DateFormatter('%Hh'))
		for label in ax.xaxis.get_ticklabels(which='both'):
			label.set_horizontalalignment('left')
		axes.yaxis.set_major_formatter('{x:.0f} km')
		axes.tick_params(which='both', length=0)

	g = satellite.at(tf)
	valid = [m is None for m in g.message]
	x1 = tf.utc_datetime()
	y1 = np.where(valid, g.distance().km - earth_radius_km, np.nan)
	ax.plot(x1, y1)
	ax.grid(which='both')
	ax.set(title=f'{selected}: altitude above sea level', xlabel='UTC')
	label_dates_and_hours(ax)
	plt.show()


show_data = ttk.Button(
   root, 
   text="Display data for satellite", 
   command=get_info
)

show_data.pack(pady=45)

root.mainloop()