import pandas as pd
import matplotlib.pyplot as plt
import csv
from skyfield.api import EarthSatellite, load
import datetime
from datetime import datetime
import pytz
from pytz import timezone
from skyfield.api import wgs84
import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter.messagebox import showerror, showwarning, showinfo

ts = load.timescale()
t = ts.now()
max_days = 7.0
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
    by_name = {sat.name: sat for sat in sats}
    satellite = by_name[f'{selected}']

show_data = ttk.Button(
   root, 
   text="Display data for satellite", 
   command=get_info
)

show_data.pack(pady=45)

root.mainloop()