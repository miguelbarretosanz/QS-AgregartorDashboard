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
from bokeh.layouts import column, widgetbox
from bokeh.models import HoverTool, CustomJS, Slider
from bokeh.io import curdoc
from bokeh.models.widgets import Select

#Import modules for conversions to radians.
import math
#Import modules for time management and time zones
import time


#GETING DATA

#Read data from Life Cycle format
LC_data = pd.read_csv('../data/Life Cycle/example/LC_export 3.csv')

#END -- GETING DATA


#PLOTING GRAPH
#size of the whole graphic
width = 700
height = 700

#List of the plots which will use hover
hover = HoverTool(names=["anular_wedges"])

p = figure(plot_width=width, plot_height=height, title="",
    x_axis_type=None, y_axis_type=None,
    x_range=(-420, 420), y_range=(-420, 420),
    min_border=0, outline_line_color="white",
    background_fill_color="#ffffff",
    tools=[hover])

hover = HoverTool(tooltips = [("Name", "name")])

p.xgrid.grid_line_color = None
p.ygrid.grid_line_color = None

#First ring (fr) parameters
fr_inner_radius = 140
fr_outer_radius = 200

#Second ring (sr) parameters
sr_inner_radius = fr_outer_radius+2
sr_outer_radius = fr_outer_radius+52

#third ring (tr) parameters
tr_inner_radius = fr_outer_radius+52+2, 
tr_outer_radius = fr_outer_radius+52+2+42

def plot_ring(ring_number, start_time, duration, label, color, h_color):
    "Create costumized annular_wedges. start_time in HH:MM:SS"
    if ring_number == 1:
        iner_radio = fr_inner_radius
        outer_radio = fr_outer_radius
    elif ring_number == 2:
        iner_radio = sr_inner_radius
        outer_radio = sr_outer_radius
    elif ring_number == 3:
        iner_radio = tr_inner_radius
        outer_radio = tr_outer_radius   
    else:
        print("ring_number value must be 1,2, or 3")  
      
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
    
    #The annular wedge is plotted in the direccion "anticlock". I tried to use 
    #the diection "clock" (which seems more 
    #logic for this plot) but I had some problems in the hit-testing. 
    #So I confirmed that it was a issue reported
    # with direction "clock : https://github.com/bokeh/bokeh/issues/2080

    p.annular_wedge(
        0, 0, iner_radio, outer_radio, hour_in_radians_to_plot - hour_rad_duration, 
        duration_in_radians_to_plot - hour_rad_duration, 
        color=color, hover_color=h_color , name="anular_wedges"
    ) 
    #Show the activity
    return p
    

##example
data1 = LC_data['START DATE(UTC)'][1]
#Parse string into a naive datetime object.
LCday,LCtime = data1.split(" ",1)

data2 = LC_data['START DATE(UTC)'][3]
#Parse string into a naive datetime object.
LCday2,LCtime2 = data2.split(" ",1)

data3 = LC_data['START DATE(UTC)'][4]
#Parse string into a naive datetime object.
LCday3,LCtime3 = data3.split(" ",1)

#First ring
#plot_ring(1,LCtime,LC_data[' DURATION'][1],"label","cyan","magenta")
#Second ring
#plot_ring(1,LCtime2,LC_data[' DURATION'][3],"label","red","pink")
#Third ring
#plot_ring(1,LCtime3,LC_data[' DURATION'][4],"label","green","grey")

#PLOT CLOCK

clock_hours_to_plot = list(range(0,24))
angles = 2*np.pi/24*pd.Series(list(range(0,24)))

def hours_axes():
    # radial axes
    p.annular_wedge(0, 0, fr_inner_radius, tr_outer_radius, angles, angles, 
                    color="lightgrey")

hours_axes()
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
p.text(xr, yr, pd.Series(labels_24h_clock), angle=label_angle,
       text_font_size="9pt", text_align="center", text_baseline="middle", 
       text_color="lightgrey")


#END -- PLOTING GRAPH




#END -- CODE FOR THE INTEACTIVE PLOT
#CODE FOR THE INTEACTIVE PLOT

#slider to change the plot size
callback = CustomJS(args=dict(xr=p.x_range),code="""
    var a = -420;

    //the model that triggered the callback is cb_obj:
    var b = cb_obj.value;

    //models passed as args are automagically available
    xr.start = a;
    xr.end = b;
    
""")

# execute a callback whenever p.x_range.start changes
p.x_range.js_on_change('start', callback)
slider_x_range = Slider(start=10, end=1000, value=1, step=10, title="x_range", 
                        callback=callback)



def update_plot(attrname, old, new):
    timestamp = select_timestamp.value
    duration_index = (np.where(LC_data['START DATE(UTC)']== timestamp)[0])
    LCday,LCtime = timestamp.split(" ",1)
    #It can be improved by using a function that "clean"  the graphic 
    #before ploting the new one.
    plot_ring(1,LCtime,86399,"label","white","white")
    plot_ring(1,LCtime,LC_data[" DURATION"][duration_index[0]],
              LC_data[" NAME"][duration_index[0]],"red","blue")
    hours_axes()
    
#Timestamp selection
select_timestamp = Select(title="Datastamp", value="foo", 
                          options=pd.Series.tolist(LC_data['START DATE(UTC)']))
select_timestamp.on_change('value', update_plot)

#SHOW ALL ON SERVER
curdoc().add_root(column(slider_x_range, widgetbox(select_timestamp),p))

