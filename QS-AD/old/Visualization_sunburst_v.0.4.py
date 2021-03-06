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
from bokeh.layouts import row, column
from bokeh.models import HoverTool, ColumnDataSource, Select
from bokeh.io import curdoc
#Import modules for conversions to radians.
import math
#Import modules for time management and time zones
import time, datetime
#Color palette
import seaborn as sns

def make_plot(source):
    
    hover = HoverTool(
            names=["anular_wedges"],
            tooltips=[
    ("Activity", "@Name"),
    ("color", "@color"),
    ])
    
    plot = figure(width=700, height=700,tools=[hover], title="",x_axis_type=None, y_axis_type=None, x_range=(-420, 420), y_range=(-420, 420),
                  min_border=0, outline_line_color="white", background_fill_color="#ffffff",)
    
    plot.annular_wedge(x=0, y=0, inner_radius='inner_radius', outer_radius='outer_radius',start_angle='start_angle', end_angle='end_angle', 
                       color='color', alpha=0.7, hover_color="lightgrey", source=source,name="anular_wedges")
    
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

def get_dataset (src, unique_days_list, selected_day):
    
    def calculate_angles(start_time,duration):
        #Convert HH:MM:SS format in radians 
        ts = time.strptime(start_time, "%H:%M:%S") 
        hour = (ts[3] + (ts[4]/60) + (ts[5]/3600))
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
    
    index_hours_same_day = np.where(unique_days_list==datetime.datetime.strptime(selected_day, "%Y-%m-%d").date())
    events_at_day = LC_data.Start_Date[list(index_hours_same_day[0][:])]
    
    start_time_list_to_plot = events_at_day.dt.time
    start_time_list_to_plot_dt = start_time_list_to_plot.to_frame()
    duration_list_to_plot = src.iloc[events_at_day.index[:],[4]]
    names_list_to_plot = src.iloc[events_at_day.index[:],[5]]
    
    #create a dataframe with the values to plot
    duration_list_to_plot.reset_index(drop=True, inplace=True)
    names_list_to_plot.reset_index(drop=True, inplace=True)
    start_time_list_to_plot_dt.reset_index(drop=True, inplace=True)
    
    result = pd.concat([duration_list_to_plot, names_list_to_plot], axis=1)
    result2 = pd.concat([result,start_time_list_to_plot_dt] , axis=1)
    
    df_start_end_angle = pd.DataFrame(index=range(0,result2.index.size),columns=['start_angle','end_angle'])

    for i in range(0, result2.index.size):
        s_d = str(result2.iloc[i]['Start_Date'])
        du = result2.iloc[i]['Duration']
        angles = calculate_angles(s_d,du)
        df_start_end_angle['start_angle'][i]= angles[0]
        df_start_end_angle['end_angle'][i] = angles[1]
    
    df_inner_outer_radius = pd.DataFrame(index=range(0,result2.index.size),columns=['inner_radius','outer_radius'])
    df_colors = pd.DataFrame(index=range(0,result2.index.size),columns=['color'])
        
    for i in range(0, result2.index.size):
        df_inner_outer_radius['inner_radius'][i]= fr_inner_radius
        df_inner_outer_radius['outer_radius'][i] = fr_outer_radius
    
    #colors
    palette = sns.color_palette("Set3", result2.index.size)
    palette = palette.as_hex()
       
    for i in range(0, result2.index.size):      
        df_colors['color'][i]= palette[i]
           
    final_df = pd.concat([df_start_end_angle,df_colors,df_inner_outer_radius,names_list_to_plot] , axis=1)
    
    return ColumnDataSource(data=final_df)
  
def update_plot(attrname, old, new):
    selected_day = select_day.value
    src = get_dataset(LC_data,unique_days_list,selected_day)
    source.data.update(src.data)

#Fixed plot's atributes  
    
#First ring (fr) parameters
fr_inner_radius = 140
fr_outer_radius = 200    
#Second ring (sr) parameters
sr_inner_radius = fr_outer_radius+2
sr_outer_radius = fr_outer_radius+52
#third ring (tr) parameters
tr_inner_radius = fr_outer_radius+52+2, 
tr_outer_radius = fr_outer_radius+52+2+42

LC_data = pd.read_csv('../data/Life Cycle/example/LC_export 3.csv')
#Columns names were changed because the orinals have some espaces and special characters
# that makes more complicated the string manipulation. For instace : ' NAME' , 'START DATE(UTC)'.
LC_data.columns = ['Start_Date', 'End_Date','Start_Time','End_time','Duration','Name','Location']
#Convert 'Start_Date' to datetime64[ns] to use pands Time Series / Date functionality.
LC_data['Start_Date'] = pd.to_datetime(LC_data.Start_Date)

#Get all the timestamps per a unique selected day
unique_days_list = LC_data.Start_Date.dt.date
index_hours_same_day = np.where(unique_days_list==unique_days_list.unique()[2])
index_hours_same_day[0][4]
events_at_day = LC_data.Start_Date[list(index_hours_same_day[0][:])]
#Create a dataframe to store unique_days_list in 
columns_ud = ['Unique_Days']
New_data_days_unique = pd.DataFrame(unique_days_list.index,columns=columns_ud)
for i in New_data_days_unique.index:
    New_data_days_unique['Unique_Days'][i]= pd.Timestamp.strftime(unique_days_list[i],'%Y-%m-%d')
#List to be shown in the "select button"
List_to_select_days = sorted(list(set(New_data_days_unique['Unique_Days'])))

selected_day='2017-01-22'
source=get_dataset(LC_data,unique_days_list,selected_day)
plot = make_plot(source)

#Timestamp selection
select_day = Select(title="Day", value="foo", options=List_to_select_days)
select_day.on_change('value', update_plot)

controls = column(select_day)
curdoc().add_root(row(plot, controls))
curdoc().title = "Sunburst"