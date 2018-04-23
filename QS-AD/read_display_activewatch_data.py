#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr  3 17:12:50 2018

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

import requests
#Import modules for time management and time zones
import dateutil.parser
import numpy as np
import pandas as pd
import time
import math as math
import seaborn as sns
import json
import pytz

from math import log, sqrt
from bokeh.plotting import figure
from bokeh.models import HoverTool, ColumnDataSource, Select
from bokeh.io import curdoc
from bokeh.layouts import row, column


def make_plot_aw(source):
    """
    Plot the annular wedges

    Parameters
    ----------
    source : Type ColumnDataSources. It contains :
        
        start_angle -- parameter for the annular_wedge
        end_angle -- parameter for the annular_wedge
        color -- parameter for the annular_wedge
        inner_radius -- parameter for the annular_wedge    
        outer_radius --  parameter for the annular_wedge   
        Name -- Activity names   
        

    Returns
    -------
    return : Figure
    """
    
    hover = HoverTool(
            names=["anular_wedges"],
            tooltips=[
    ("Activity", "@Name"),
    ("color", "@color"),
    ])
    
    plot = figure(width=700, height=700,tools=[hover], title="",x_axis_type=None, y_axis_type=None, x_range=(-420, 420), y_range=(-420, 420),
                  min_border=0, outline_line_color="white", background_fill_color="#ffffff",)
    
    plot.annular_wedge(x=0, y=0, inner_radius='inner_radius', outer_radius='outer_radius',start_angle='start_angle', end_angle='end_angle', 
                       color='color', alpha=0.9, hover_color='color',hover_line_color="black", hover_alpha = 0.5, source=source,name="anular_wedges",legend='Name')
    
    #Fixed attributes
    plot.xgrid.grid_line_color = None
    plot.ygrid.grid_line_color = None
    
    #plot clock
    angles = 2*np.pi/24*pd.Series(list(range(0,24)))
    plot.annular_wedge(0, 0, fr_inner_radius, tr_outer_radius, angles, angles, color="lightgrey")
    
    # Plot clock labels (24 hours)
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
    plot.text(xr, yr, pd.Series(labels_24h_clock), angle=label_angle, text_font_size="9pt", text_align="center", text_baseline="middle", 
       text_color="lightgrey")
    
    return plot


def calculate_angles_aw(start_time, duration):
    
    #Example  time.struct_time   = time.struct_time(tm_year=2018, tm_mon=3, tm_mday=15, tm_hour=20, tm_min=53, tm_sec=31, tm_wday=3, tm_yday=74, tm_isdst=0)
    #thus tm_hour correspond to start_time[3] etc...
    hour = (start_time[3] + (start_time[4]/60) + (start_time[5]/3600))
    hour_rad = math.radians(hour * 15.0)
    #add "pi/2" to transform radians to a 24 hours clock form.
    hour_in_radians_to_plot = -hour_rad + np.pi/2
            
    #Use duration and convert seconds in radians
    sec_rad = time.gmtime(duration)
    hour_duration = (sec_rad[3] + (sec_rad[4]/60) + (sec_rad[5]/3600))
    hour_rad_duration = math.radians(hour_duration * 15.0)
    duration_in_radians_to_plot = (hour_in_radians_to_plot + hour_rad_duration)
    
    start_angle= hour_in_radians_to_plot - hour_rad_duration
    end_angle= duration_in_radians_to_plot - hour_rad_duration
            
    return start_angle, end_angle


def get_data_aw(events, day_selected):
    
    #Group all the events from the same day
    index_hours_same_day = np.where(events.date == day_selected)
    index_hours_same_day = list(index_hours_same_day)
    events_at_day = events.loc[list(index_hours_same_day[0]),:]

    final_df = pd.DataFrame({ 'start_angle' : events_at_day['start_angle'],
                         'end_angle' : events_at_day['end_angle'],
                         'color': events_at_day['color'],
                         'Name' : events_at_day['Name'],
                         'inner_radius' : events_at_day['inner_radius'], 
                         'outer_radius' : events_at_day['outer_radius'], 
        })
    return ColumnDataSource(data=final_df)


def activities_color_table (array_activities):
    df_activity_colors = pd.DataFrame(index=range(0,array_activities.size,1),columns=['Activities','Colors'])
    #create palette
    pal2 = sns.color_palette('pastel').as_hex()
    pal3 = sns.color_palette("Set1", 10).as_hex()
    pal4 = sns.color_palette("Set2", 10).as_hex()
    pal5 = sns.color_palette("Set3", 10).as_hex()
    pal6 = sns.color_palette("BrBG", 7).as_hex()
    pal7 = sns.color_palette("RdBu_r", 7).as_hex()
    pal8 = sns.color_palette("coolwarm", 7).as_hex()
    pal9 = sns.diverging_palette(10, 220, sep=80, n=7).as_hex()   
    palette = np.concatenate((pal2,pal3,pal4,pal5,pal6,pal7,pal8,pal9), axis=0)
       
    for i in range(0,array_activities.size,1):
        df_activity_colors['Activities'][i]=array_activities[i]
        df_activity_colors['Colors'][i] = palette[i]
        
    return df_activity_colors


def data_source(raw_data_source):
    if raw_data_source == 'localhost':
        # api-endpoint
        URL = "http://127.0.0.1:5600/api/0/buckets/aw-watcher-window_macbook-pro-4.home/events"
        # location given here
        location = "Localhost"
        # defining a params dict for the parameters to be sent to the API
        PARAMS = {'address':location}
        # sending get request and saving the response as response object
        r = requests.get(url = URL, params = PARAMS)
        data = r.json()

    elif raw_data_source == 'local_file':
        data = json.load(open("../data/ActivityWatch/22-04-2018_aw-event-export-aw-watcher-window_MacBook-Pro-4.local.json"))   
        
    else: 
        print("Not data source defined. Please write localhost or local_file")
    return(data)
  
def update_plot_aw(attrname, old, new):
    selected_date = select_date.value
    src = get_data_aw(DT_events, selected_date)
    source.data.update(src.data)
    print(src.data)
    print(selected_date)
    

    
def utc_to_local(utc_dt):
    local_tz = pytz.timezone('Europe/Paris') 
    local_dt = utc_dt.replace(tzinfo=pytz.utc).astimezone(local_tz)
    return local_tz.normalize(local_dt)


#Fixed plot's atributes  
fr_inner_radius = 140 #First ring (fr) parameters
fr_outer_radius = 200    
sr_inner_radius = fr_outer_radius+2 #Second ring (sr) parameters
sr_outer_radius = fr_outer_radius+52
tr_inner_radius = fr_outer_radius+52+2, #third ring (tr) parameters
tr_outer_radius = fr_outer_radius+52+2+42

data_s = data_source('local_file')

#Create dataframe with the necesary data to generate the plot
DT_events = pd.DataFrame(index=range(0,len(data_s)),columns=[ 'Name', 'duration', 'timestamp', 'start_angle', 
                         'end_angle','inner_radius','outer_radius','color','date'])

    
for i in range(0, len(data_s)):
        DT_events['Name'][i] = data_s[i]["data"]['app']
        DT_events['duration'][i] = data_s[i]["duration"]
        DT_events['timestamp'][i] = data_s[i]["timestamp"]
        
        #calculate start time and end time to calculate the angles
        datatime_timestamp = dateutil.parser.parse(data_s[i]["timestamp"])
        datatime_timestamp = utc_to_local(datatime_timestamp)
        start_time = datatime_timestamp.timetuple()
        angles = calculate_angles_aw(start_time,data_s[i]["duration"])
       
        DT_events['start_angle'][i] = angles[0]
        DT_events['end_angle'][i] = angles[1]
        DT_events['inner_radius'][i] = sr_inner_radius
        DT_events['outer_radius'][i] = sr_outer_radius
        DT_events['color'][i] = "red"
        DT_events['date'][i] = str(start_time[0]) + "-" + str(start_time[1]) + "-" + str(start_time[2])

df_activity_colors = activities_color_table(DT_events.Name.unique())
#Match events with its respective color code
df_colors = pd.DataFrame(index=range(0,DT_events.Name.index.size),columns=['color'])
for i in range(0,DT_events.Name.index.size):
    df_colors.color[i] = df_activity_colors.Colors[np.where(DT_events.Name[i] == df_activity_colors.Activities)[0][0]]

for i in range(0, len(data_s)):
    DT_events['color'][i] = df_colors.color[i]

#Create a dataframe to store unique_days_list to use in the "select menu" 
unique_dates = sorted(list(DT_events.date.unique()))

selected_day = '2018-4-10'
source = get_data_aw(DT_events, selected_day)
plot_aw = make_plot_aw(source)

#Timestamp selection
select_date = Select(title="Day", value="foo", options=unique_dates)
select_date.on_change('value', update_plot_aw)
            
controls_aw = column(select_date)
curdoc().add_root(row(plot_aw, controls_aw))
curdoc().title = "Activity Watch Viz"
