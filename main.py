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
from tkinter import ttk
from tkinter.messagebox import showinfo

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

root = tk.Tk()

root.geometry('300x200')
root.resizable(False, False)
root.title('Combobox Widget')

label = ttk.Label(text="Please select a Satellite:")
label.pack(fill=tk.X, padx=5, pady=5)

selected_sat = tk.StringVar()
sat_cb = ttk.Combobox(root, textvariable=selected_sat)

sat_cb['values'] = names

sat_cb.pack(fill=tk.X, padx=5, pady=5)

def sat_changed(event):
    """ handle the sat changed event """
    showinfo(
        title='Result',
        message=f'You selected {selected_sat.get()}!'
    )

sat_cb.bind('<<ComboboxSelected>>', sat_changed)

root.mainloop()