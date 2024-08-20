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
def add_plus(string, index):
	if string[index] != '-':
		return string[:index] + '+' + string[index:]
def location_lookup():
  try:
    return json.load(urlopen('http://ipinfo.io/json'))
  except urlopen.HTTPError:
    return False
location = location_lookup()
bluffton = str(location['loc'])
bluffton = add_plus(bluffton, 0)
bluffton = add_plus(bluffton, 5)
print(bluffton)
t0 = t
t1 = t+1

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
	my_list = Listbox(new_win, width=50)
	my_list.pack(pady=30)

	t = ts.now()
	by_name = {sat.name: sat for sat in sats}
	satellite = by_name[f'{selected}']
	days = t - satellite.epoch
	if days > 0:
		time_epoch = '{:.3f} days past epoch'.format(days)
	else:
		time_epoch = '{:.3f} days until epoch'.format(abs(days))
	geocentric = satellite.at(t)
	lat, lon = wgs84.latlon_of(geocentric)
	t, events = satellite.find_events(bluffton, t0, t1, altitude_degrees=30.0)
	event_names = 'rise above 30°', 'culminate', 'set below 30°'
	for ti, event in zip(t, events):
		name = event_names[event]
		print(ti.utc_strftime('%Y %b %d %H:%M:%S'), name)
	
	my_list.insert(END, time_epoch)
	my_list.insert(END, f'Latitude: {lat}')
	my_list.insert(END, f'Longitude: {lon}')

show_data = ttk.Button(
   root, 
   text="Display data for satellite", 
   command=get_info
)

show_data.pack(pady=45)

root.mainloop()