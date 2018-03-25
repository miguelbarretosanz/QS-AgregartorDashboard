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
import pytz
from pytz import timezone
#Color palette
import seaborn as sns


def make_plot(source):
    """
    Plot the annular wedges

    Parameters
    ----------
    source : ColumnDataSources

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

def get_dataset (src, unique_days_list, selected_day, df_activity_colors):
    
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
    
    #Group events from the same day
    index_hours_same_day = np.where(unique_days_list==datetime.datetime.strptime(selected_day, "%Y-%m-%d").date())
    events_at_day = src.Start_Date_UTC[list(index_hours_same_day[0][:])]
    
    #Time zones hours correction
    events_at_day = events_at_day.dt.tz_localize('UTC')
    #Get the time zone from "Start_Time_Local"
    get_tz = LC_data.Start_Time_Local[index_hours_same_day[0][0]].split(" ")
    time_zone = get_tz[3] 
    events_at_day = events_at_day.dt.tz_convert(time_zone)
  
    start_time_list_to_plot = events_at_day.dt.time
    start_time_list_to_plot_dt = start_time_list_to_plot.to_frame()
    duration_list_to_plot = src.iloc[events_at_day.index[:],[4]]
    events_list_to_plot = src.iloc[events_at_day.index[:],[5]]
    
    #create dataframe with the parameters to plot function
    duration_list_to_plot.reset_index(drop=True, inplace=True)
    events_list_to_plot.reset_index(drop=True, inplace=True)
    start_time_list_to_plot_dt.reset_index(drop=True, inplace=True)
    
    result = pd.concat([duration_list_to_plot, events_list_to_plot], axis=1)
    result2 = pd.concat([result,start_time_list_to_plot_dt] , axis=1)
    
    df_start_end_angle = pd.DataFrame(index=range(0,result2.index.size),columns=['start_angle','end_angle'])

    for i in range(0, result2.index.size):
        s_d = str(result2.iloc[i]['Start_Date_UTC'])
        du = result2.iloc[i]['Duration']
        angles = calculate_angles(s_d,du)
        df_start_end_angle['start_angle'][i]= angles[0]
        df_start_end_angle['end_angle'][i] = angles[1]
    
    df_inner_outer_radius = pd.DataFrame(index=range(0,result2.index.size),columns=['inner_radius','outer_radius'])
        
    for i in range(0, result2.index.size):
        df_inner_outer_radius['inner_radius'][i]= fr_inner_radius
        df_inner_outer_radius['outer_radius'][i] = fr_outer_radius
    
    #Match events with its respective color code
    df_colors = pd.DataFrame(index=range(0,events_list_to_plot.index.size),columns=['color'])
    for i in range(0,events_list_to_plot.index.size):
        df_colors.color[i] = df_activity_colors.Colors[np.where(events_list_to_plot.Name[i] == df_activity_colors.Activities)[0][0]]
           
    final_df = pd.concat([df_start_end_angle,df_colors,df_inner_outer_radius,events_list_to_plot] , axis=1)
    
    return ColumnDataSource(data=final_df)
  
def update_plot(attrname, old, new):
    selected_day = select_day.value
    src = get_dataset(LC_data,unique_days_list,selected_day,df_activity_colors)
    source.data.update(src.data)

def activities_color_table (array_activities):
    df_activity_colors = pd.DataFrame(index=range(0,array_activities.size,1),columns=['Activities','Colors'])
    #Palette from https://stackoverflow.com/questions/33295120/how-to-generate-gif-256-colors-palette
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
        
#Fixed plot's atributes  
fr_inner_radius = 140 #First ring (fr) parameters
fr_outer_radius = 200    
sr_inner_radius = fr_outer_radius+2 #Second ring (sr) parameters
sr_outer_radius = fr_outer_radius+52
tr_inner_radius = fr_outer_radius+52+2, #third ring (tr) parameters
tr_outer_radius = fr_outer_radius+52+2+42

LC_data = pd.read_csv('../data/Life Cycle/example/LC_export 3.csv')
#Columns names were changed because the orinals have some espaces and special characters
# that makes more complicated the string manipulation. For instace : ' NAME' , 'START DATE(UTC)'.
LC_data.columns = ['Start_Date_UTC', 'End_Date_UTC','Start_Time_Local','End_time_Local','Duration','Name','Location']
#Convert 'Start_Date' to datetime64[ns] to use pands Time Series / Date functionality.
#To-do : the function "to_datetime" in converting 'Start_Time_Local' to UTC I wanto to keep in local time.
LC_data['Start_Date_UTC'] = pd.to_datetime(LC_data.Start_Date_UTC)  

#Get all the events' timestamps per unique selected day
unique_days_list = LC_data.Start_Date_UTC.dt.date
index_hours_same_day = np.where(unique_days_list==unique_days_list.unique()[2])
index_hours_same_day[0][4]
events_at_day = LC_data.Start_Date_UTC[list(index_hours_same_day[0][:])]
#Create a dataframe to store unique_days_list in 
columns_ud = ['Unique_Days']
New_data_days_unique = pd.DataFrame(unique_days_list.index,columns=columns_ud)
for i in New_data_days_unique.index:
    New_data_days_unique['Unique_Days'][i]= pd.Timestamp.strftime(unique_days_list[i],'%Y-%m-%d')
#List to be shown in the "select button"
List_to_select_days = sorted(list(set(New_data_days_unique['Unique_Days'])))

#Colors table per activity
df_activity_colors = activities_color_table(LC_data.Name.unique())


selected_day='2017-01-22'
source=get_dataset(LC_data,unique_days_list,selected_day,df_activity_colors)
plot = make_plot(source)

#Timestamp selection
select_day = Select(title="Day", value="foo", options=List_to_select_days)
select_day.on_change('value', update_plot)

controls = column(select_day)
curdoc().add_root(row(plot, controls))
curdoc().title = "Sunburst"