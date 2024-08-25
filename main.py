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

ts = load.timescale() # loads the timescale
t = ts.now() # sets when "now" is
max_days = 1.0 # how many days must pass before data is re-downloaded
names = [] # creates an empty list called names
name = 'satellites.csv' # the filename for the data
base = 'https://celestrak.org/NORAD/elements/gp.php' # base of the url
url = base + '?GROUP=active&FORMAT=csv' # the full url for data
# downloads the data if the file doesnt exist or it hasnt been reloaded in longer than max days specifies
if not load.exists(name) or load.days_old(name) >= max_days:
    load.download(url, filename=name)
# creates the data and fills the names list
with load.open('satellites.csv', mode='r') as f:
    data = list(csv.DictReader(f))
    for row in data:
        names.append(row['OBJECT_NAME'])
sats = [EarthSatellite.from_omm(ts, fields) for fields in data] # a list of all satellites and some basic data for them
names.sort() # sorts all satellites by alphabetical order
# gets the latitude and longitude of the user for more accurate data
def location_lookup():
  try:
    return json.load(urlopen('http://ipinfo.io/json'))
  except:
    return {"loc": "0, 0"}
location = location_lookup()
place = str(location['loc'])
comma = place.index(',')
lat = float(place.split(',')[0]) # defines latidue
lon = float(place.split(',')[1]) # defines longitude
bluffton = wgs84.latlon(lat, lon) # converts the latitude and longitude into data for skyfield
t0 = t # t0 is now, used in code later
t1 = t+1 # one l=day later than now, used in code later
earth_radius_km = 6371.0 # earths radius

# all the gui stuff
root = Tk()
root.title('Satellite Data Program') # the title of the main window
root.geometry("500x500") # the size of the main window

# will update the listbox to contain all the satellites
def update(data):
	my_list.delete(0, END)

	for item in data:
		my_list.insert(END, item)

# fills out searchbox when a satellite in the listbox is clicked
def fillout(e):
	my_entry.delete(0, END)

	my_entry.insert(0, my_list.get(ANCHOR))
	global selected
	selected = my_list.get(ANCHOR) # creates a variable with the name of the selected ssatellite

# will update the listbox based on what is in the searchbox
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

# text in the main window
my_label = Label(root, text="Search For A Satellite",
	font=("Helvetica", 14), fg="grey")

my_label.pack(pady=20)

# the searchbox
my_entry = Entry(root, font=("Helvetica", 20))
my_entry.pack()

# the listbox
my_list = Listbox(root, width=50)
my_list.pack(pady=40)

update(names)

my_list.bind("<<ListboxSelect>>", fillout) # the command bindings for the listbox

my_entry.bind("<KeyRelease>", check) # the command bindings for the searchbox

# the function that displays all the data
def get_info():
	new_win = Toplevel(root) # creates a new window above the current one
	new_win.title('Satellite Data') # the new windows name
	new_win.geometry('400x400') # the new windows geometry
	Label(new_win, text=f"Data For {selected}",font=("Helvetica", 20)).pack(pady=20) # text in the new window
	my_list = Listbox(new_win, width=70) # listbox in the new window
	my_list.pack(pady=30)
	
	t = ts.now() # defines "now"
	# selects satellite based off its name
	by_name = {sat.name: sat for sat in sats}
	satellite = by_name[f'{selected}']
	tf = ts.tt_jd(np.arange(satellite.epoch.tt - 1.0, satellite.epoch.tt + 1.0, 0.005)) # a timeframe for the graph
	days = t - satellite.epoch # days to or past epoch
	if days > 0:
		time_epoch = '{:.3f} days past epoch'.format(days)
	else:
		time_epoch = '{:.3f} days until epoch'.format(abs(days))
	geocentric = satellite.at(t) # geocentric coordiantes of the satellite
	lat, lon = wgs84.latlon_of(geocentric) # latitude and longitude of the satellite
	v = geocentric.velocity.km_per_s # the velocity of the satellite
	speed = math.sqrt(pow(v[0], 2)+pow(v[1], 2)+pow(v[2], 2)) # the speed of the satellite

	my_list.insert(END, time_epoch) # inserts the epoch into the listbox
	my_list.insert(END, f'Current Speed: {round(speed, 3)}km/s') # inserts the satellites speed into the lisbox
	my_list.insert(END, f'Current Latitude: {lat}') # inserts the latidue of the satellite into the listbox
	my_list.insert(END, f'Current Longitude: {lon}') # inserts the longitude of the satellite into the listbox
	my_list.insert(END, f'How many times {selected} will be over 30° in the next day:') # adds text into the listbox

	t = ts.now() # defines "now"
	# shows how many times the satellite will be over 30° in the sky over the next day from the users location, and whether it will be sunlit or not
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
		
	t = ts.now() # defines "now"
	difference = satellite - bluffton # gets the difference in postitions
	topocentric = difference.at(t) # defines the topocentric coordinates of the satellite
	alt, az, distance = topocentric.altaz() # defines the altitude (degrees), azimuth (degrees) and distance from the user of the satellite

	my_list.insert(END, f'Where {selected} is in the sky:') # adds text to the listbox

	# adds text saying if the satellite is above or below the horizon into the listbox
	if alt.degrees > 0:
		my_list.insert(END, f'{selected} is above the horizon')
	else:
		my_list.insert(END, f'{selected} is below the horizon')

	my_list.insert(END, f'Altitude: {alt}') # inserts the altitude (degrees) into the listbox
	my_list.insert(END, f'Azimuth: {az}') # inserts the azimuth (degreees) into the listbox
	my_list.insert(END, 'Distance: {:.1f} km'.format(distance.km)) # inserts the distance from the user of the satellite into the lisbox

	# puts dates on the x axis of the graph
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

	g = satellite.at(tf) # gets all postitions of the satellite over the timeframe
	valid = [m is None for m in g.message] # defines valid g positions
	x1 = tf.utc_datetime() # defines the x axis, which is the date and time
	y1 = np.where(valid, g.distance().km - earth_radius_km, np.nan) # defines the y axis, which is the satellites altitude above sea level
	ax.plot(x1, y1) # plots the x and y axis
	ax.grid(which='both') # creates a grid on the graph
	ax.set(title=f'{selected}: altitude above sea level', xlabel='UTC', ylabel='Altidute (km)') # creates a title, x axis label and y axis label
	label_dates_and_hours(ax) # adds the date and time along the x axis
	plt.show() # shows the graph


# defines the show satelite sata button
show_data = ttk.Button(
   root, 
   text="Display data for satellite", 
   command=get_info
)

show_data.pack(pady=45)

root.mainloop() # keeps the gui open

# the 200th line of this code :3