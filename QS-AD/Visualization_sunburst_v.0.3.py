#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 21 07:16:35 2018

@author: MiguelArturo
"""

__author__ = "Miguel Barreto Sanz"
__copyright__ = "Copyright 2018, Miguel Barreto Sanz"
__credits__ = ["Miguel Barreto Sanz"]
__license__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "Miguel Barreto Sanz"
__email__ = "miguelbarretosanz@gmail.com"
__status__ = "Development"

from math import log, sqrt
import numpy as np
import pandas as pd
from bokeh.plotting import figure


#Import modules for interactive graphics
from bokeh.layouts import row, column, widgetbox
from bokeh.models import HoverTool, CustomJS, Slider, ColumnDataSource, Select
from bokeh.io import curdoc

#Import modules for conversions to radians.
import math
#Import modules for time management and time zones
import time

def make_plot(source):
    
    hover = HoverTool(
            names=["anular_wedges"],
            tooltips=[
    ("Activity", "@Activity_name"),
    ("(ir,or)", "(@inner_radius, @outer_radius)"),
    ("color", "@color"),
    ])
    
    plot = figure(width=700, height=700,tools=[hover], title="",x_axis_type=None, 
                  y_axis_type=None, x_range=(-420, 420), y_range=(-420, 420),
                  min_border=0, outline_line_color="white",
                  background_fill_color="#ffffff",)
    
    plot.annular_wedge(x=0, y=0, inner_radius='inner_radius', outer_radius='outer_radius',
                start_angle='start_angle', end_angle='end_angle', color='color', 
                alpha=0.6, hover_color="lightgrey", source=source,name="anular_wedges")
    
    #Fixed attributes
    plot.xgrid.grid_line_color = None
    plot.ygrid.grid_line_color = None
    
    #plot clock
    angles = 2*np.pi/24*pd.Series(list(range(0,24)))
    plot.annular_wedge(0, 0, fr_inner_radius, tr_outer_radius, angles, angles, 
                    color="lightgrey")
    # hours labels
    labels = np.power(10.0, np.arange(-3, 4))
    minr = sqrt(log(.001 * 1E4))
    maxr = sqrt(log(1000 * 1E4))
    a = ((tr_outer_radius + 10) - fr_inner_radius) / (minr - maxr)
    b = fr_inner_radius - a * maxr
    radii = a * np.sqrt(np.log(labels * 1E4)) + b
    xr = radii[0]*np.cos(np.array(angles))
    yr = radii[0]*np.sin(np.array(angles))
    label_angle=np.array(angles)
    label_angle[label_angle < -np.pi/2] += np.pi # easier to read labels on the left side
    labels_24h_clock = list(range(6,-1,-1)) + list(range(23,6,-1))
    plot.text(xr, yr, pd.Series(labels_24h_clock), angle=label_angle,
       text_font_size="9pt", text_align="center", text_baseline="middle", 
       text_color="lightgrey")
    
    return plot


def get_dataset (src,timestamp):
    
    duration_index = np.where(src['Start_Date']== timestamp)
    LCday,LCtime = timestamp.split(" ",1)
    
    start_time = LCtime
    duration = src["Duration"][duration_index[0][0]]
    activity_name= src["Name"][duration_index[0][0]]
    
    #Convert HH:MM:SS format in radians 
    ts = time.strptime(start_time, "%H:%M:%S") 
    hour = (ts[3] + (ts[4]/60) + (ts[5]/3600))
    hour_rad = math.radians(hour * 15.0)
    #add "pi/2" to transform radians to a 24 hours clock form.
    hour_in_radians_to_plot = -hour_rad + np.pi/2
    
    #Convert seconds in radians
    sec_rad = time.gmtime(duration)
    hour_duration = (sec_rad[3] + (sec_rad[4]/60))
    hour_rad_duration = math.radians(hour_duration * 15.0)
    duration_in_radians_to_plot = (hour_in_radians_to_plot + hour_rad_duration)
    
    start_angle= hour_in_radians_to_plot - hour_rad_duration
    end_angle= duration_in_radians_to_plot - hour_rad_duration
    
    df = pd.DataFrame({'start_angle':[start_angle],
                   'end_angle':[end_angle],
                   'color':["pink"],
                    'inner_radius':[fr_inner_radius],
                    'outer_radius':[fr_outer_radius],
                    'Activity_name':[activity_name],
                   })
    
    return ColumnDataSource(data=df)
  
    
def update_plot(attrname, old, new):
    timestamp = select_timestamp.value
    src = get_dataset(LC_data,timestamp)
    source.data.update(src.data)

    
#First ring (fr) parameters
fr_inner_radius = 140
fr_outer_radius = 200    
#Second ring (sr) parameters
sr_inner_radius = fr_outer_radius+2
sr_outer_radius = fr_outer_radius+52
#third ring (tr) parameters
tr_inner_radius = fr_outer_radius+52+2, 
tr_outer_radius = fr_outer_radius+52+2+42

source = ColumnDataSource(data=dict(
    inner_radius=[fr_inner_radius,sr_inner_radius,tr_inner_radius],
    outer_radius=[fr_outer_radius,sr_outer_radius,tr_outer_radius],
    start_angle=[0.0,1,2],
    end_angle=[4.8,4.9,5],
    color=["red","pink","yellow"]
))




LC_data = pd.read_csv('../data/Life Cycle/example/LC_export 3.csv')
sd_object2 =LC_data['START DATE(UTC)']
LC_data.columns = ['Start_Date', 'End_Date','Start_Time','End_time',
                       'Duration','Name','Location']
LC_data['Start_Date'] = pd.to_datetime(LC_data.Start_Date)
#sd_object =LC_data['Start_Date'].astype(object)


#get timestamp per day
unique_days_list = LC_data.Start_Date.dt.date
index_hours_same_day = np.where(LC_data.Start_Date.dt.date==unique_days_list.unique()[2])
index_hours_same_day[0][4]
evenst_at_day = LC_data.Start_Date[list(index_hours_same_day[0][:])]

columns_ud = ['Unique_Days']
New_data_days_unique = pd.DataFrame(unique_days_list.index,columns=columns_ud)

for i in New_data_days_unique.index:
    New_data_days_unique['Unique_Days'][i]= pd.Timestamp.strftime(unique_days_list[i],'%Y-%m-%d')


#from timedate to string
columns = ['Start_Date']
New_data = pd.DataFrame(index=LC_data['Start_Date'].index,columns=columns)
for i in New_data.index:
    New_data['Start_Date'][i]= pd.Timestamp.strftime(LC_data['Start_Date'][i],'%Y-%m-%d %H:%M:%S')

List_to_select = sorted(list(set(New_data_days_unique['Unique_Days'])))

List_unique = New_data_days_unique['Unique_Days'].tolist()

timestamp='2017-01-22 10:11:30'
source=get_dataset(LC_data,timestamp)
plot = make_plot(source)


#Timestamp selection
#select_timestamp = Select(title="Timestamp", value="foo", 
#                          options=List_unique)
select_timestamp = Select(title="Timestamp", value="foo", 
                          options=List_to_select)
select_timestamp.on_change('value', update_plot)


controls = column(select_timestamp)
curdoc().add_root(row(plot, controls))
curdoc().title = "Sunburst"