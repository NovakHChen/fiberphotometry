#!/usr/bin/env python
# coding: utf-8

# In[1]:


# Load Necessary Packages

get_ipython().run_line_magic('load_ext', 'autoreload')
get_ipython().run_line_magic('autoreload', '2')

import os
import tdt
import cv2
import holoviews as hv
import numpy as np
import pandas as pd
import FreezeAnalysis_Functions as fz
import matplotlib
import matplotlib.pyplot as plt

get_ipython().run_line_magic('matplotlib', 'inline')


# In[2]:


# Set Path for Fiber Photometry Data
# REMEMBER TO CHANGE mt_cutoff & FreezeThreshold

Data_path = '../nia_10_5HT_cxtA_day_2' #'../nia_10_5HT_cxtC_day_4/' #'../nia_2_5HT_cxtA_day_2/' #../nia_4_5HT_cxtA_day_2/' #'../nia_4_5HT_cxtB_day_2/'  #'../nia_6_5HT_cxtC_day_4/'
video_file = 'pattern-240604-113630_nia_10-240710-103156_Cam1.avi' #'pattern-240604-113630_nia_10-240712-153619_Cam1.avi' #'pattern-240604-113630_nia_2-240612-110743_Cam1.avi' #'pattern-240604-113630_nia_4-240612-112936_Cam1.avi' #'pattern-240604-113630_nia_4-240612-144028_Cam1.avi' #'pattern-240604-113630_nia_6-240712-151403_Cam1.avi'


# In[3]:


# Read Fiber Photometry Data

BLOCKPATH = Data_path
data = tdt.read_block(BLOCKPATH)


# In[4]:


# Set Directory and File Information For Freezing Data
video_dict = {
    'dpath'   : Data_path,  
    'file'    : video_file,
    'start'   : 0, 
    'end'     : None,
    'dsmpl'   : 1,
    'stretch' : dict(width=1, height=1)
}

# Get Behavior video information
cap = cv2.VideoCapture(os.path.join(video_dict['dpath'], video_dict['file']))
behavior_fps = cap.get(cv2.CAP_PROP_FPS)
total_behavior_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) #Total frames for behavior video
cap.release()

# Convert fiber time and TTL pulses to match behavior video frames
final_frame = ((data.info.duration.total_seconds()) * behavior_fps) # final frame of fiber recording
pulse_one = final_frame - ((data.epocs.PtC0.onset[0]) * behavior_fps) # time between 1st pulse and final_frame
pulse_two = final_frame - ((data.epocs.PtC0.onset[1]) * behavior_fps) # time between 2nd pulse and final_frame
pulse_three = final_frame - ((data.epocs.PtC0.onset[2]) * behavior_fps) # time between 3rd pulse and final_frame

# Here we are adjusting the start/end of the behavior data to match the fiber data. 
# This will be based on the second/shock pulse -> looking at 600 frames / 30 sec before and after

frames_before_shock = 600
frames_after_shock = 600

video_dict['start'] = (total_behavior_frames - (int(pulse_two) + frames_before_shock))
video_dict['end'] = (total_behavior_frames - (int(pulse_two) - frames_after_shock))


# In[5]:


print (data.epocs.PtC0.onset)
print (data.info.duration.total_seconds())
print (behavior_fps)
print (total_behavior_frames)
print (final_frame)
print (pulse_one)
print (pulse_two)
print (pulse_three)


# In[6]:


get_ipython().run_cell_magic('output', 'size=100', '# Load Freezing Video and Crop Frame if Desired\n\nimg_crp, video_dict = fz.LoadAndCrop(video_dict, cropmethod="Box")\nimg_crp')


# In[7]:


get_ipython().run_cell_magic('output', 'size=100', '\n# Set Motion Threshold for behavior Video\n\nmt_cutoff = 7\n\n# Detect Motion\n\nh,w = 300,1000 \n\nMotion = fz.Measure_Motion(video_dict, mt_cutoff, SIGMA=1) # x-axis\nMotion_time = np.arange(len(Motion))#/fps # y-axis')


# In[8]:


# Calculate offset based on time_before_shock
offset = 180 - (frames_before_shock / behavior_fps)

# Convert frame numbers to seconds and offset to match original timing
time_in_seconds = (Motion_time / behavior_fps) + offset

# Calculate x-axis limits dynamically
x_min = 180 - (frames_before_shock / behavior_fps)  # Start time
x_max = 180 + (frames_after_shock / behavior_fps)   # End time

# Plot Motion Graph
plt_mt = hv.Curve((time_in_seconds, Motion), 'Time (s)', 'Pixel Change', label='Motion').opts(
    height=h, width=w, line_width=1, color="steelblue",
    title="Motion Across Session", xlim=(x_min, x_max), padding=0.0, show_grid=False)

# Convert shock line position to seconds (always at 180s)
shock_line = hv.VLine(180, label='Shock Time').opts(
    color='red', line_dash='dashed')

# Combine plots with strict bounds
(plt_mt * shock_line).opts(
    xlabel='Time (s)',margin=0)


# In[9]:


# Set Freezing Parameters

FreezeThresh = 3500
MinDuration = 20 


# In[10]:


get_ipython().run_cell_magic('output', 'size=100', '\n# Measure Freezing\n\nh,w = 300,1000 \n\nFreezing = fz.Measure_Freezing(Motion,FreezeThresh,MinDuration)  \nfz.SaveData(video_dict,Motion,Freezing,mt_cutoff,FreezeThresh,MinDuration)\nprint(\'Average Freezing: {x}%\'.format(x=np.average(Freezing)))\n\n# Create freezing area plot with adjusted time axis\nplt_fz = hv.Area((time_in_seconds, Freezing*(Motion.max()/100)), \'Time (s)\', \'Motion\').opts(\n    color=\'lightgray\',line_width=0,line_alpha=0)\nplt_mt = hv.Curve((time_in_seconds, Motion), \'Time (s)\', \'Motion\').opts(\n    height=h,width=w,line_width=1, color=\'steelblue\',\n    title="Motion Across Session with Freezing Highlighted in Gray")\nthreshold_line = hv.HLine(y=FreezeThresh).opts(\n    color=\'red\',line_width=1,line_dash=\'dashed\')\n(plt_fz * plt_mt * threshold_line * shock_line).opts(\n    xlim=(x_min, x_max),padding=0.0,margin=0,show_grid=False)')


# In[11]:


# Create binarized freezing data
freezing_binarized = Freezing*(Motion.max()/100)
#plt.plot(freezing_binarized)

plt.figure(figsize=(12, 4))
plt.plot(time_in_seconds, freezing_binarized)
plt.axvline(x=180, color='red', linestyle='--')
plt.xlim(x_min, x_max)
plt.xlabel('Time (s)')
plt.ylabel('Motion')
plt.title('Binarized Freezing')


# In[12]:


# Generate Raw Fiber Photometry Signal

plt.plot(data['streams']['_405A']['data'])


# In[13]:


# Convert frames to seconds for window size
fiber_seconds_before = frames_before_shock/behavior_fps
fiber_seconds_after = frames_after_shock/behavior_fps

# Calculate axis limits for display
fiber_time_min = 180 - fiber_seconds_before
fiber_time_max = 180 + fiber_seconds_after


# In[14]:


# Make a time array based on the number of samples and sample freq
matplotlib.rcParams['font.size'] = 18

Serotonin = '_465A'  # Serotonin channel
ISOS = '_405A'  # Isosbestic channel
fiber_time = np.linspace(1, len(data.streams[Serotonin].data), len(data.streams[Serotonin].data))/data.streams[Serotonin].fs

# Calculate offset to make shock appear at 180s
fiber_offset = 180 - data.epocs.PtC0.onset[1]
fiber_time_offset = fiber_time + fiber_offset

# Plot both unprocessed demodulated stream
fig1 = plt.figure(figsize=(10,6))
ax0 = fig1.add_subplot(111)

# Plotting the traces with offset time
p1, = ax0.plot(fiber_time_offset, data.streams[Serotonin].data, linewidth=2, color='green', label='Serotonin')
p2, = ax0.plot(fiber_time_offset, data.streams[ISOS].data, linewidth=2, color='blueviolet', label='ISOS')

ax0.set_xlim(fiber_time_min, fiber_time_max)
ax0.axvline(x=180, color='red', linestyle='--', label='Shock')
ax0.set_ylabel('mV')
ax0.set_xlabel('Seconds')
ax0.set_title('Raw Demodulated Response')
ax0.legend(handles=[p1,p2], loc='upper right')
fig1.tight_layout()


# In[15]:


# Artifact Removal with adjusted time window
t = 8
inds = np.where(fiber_time>t)
ind = inds[0][0]
fiber_time = fiber_time[ind:]
fiber_time_offset = fiber_time + fiber_offset  # Recalculate offset time after artifact removal
data.streams[Serotonin].data = data.streams[Serotonin].data[ind:]
data.streams[ISOS].data = data.streams[ISOS].data[ind:]

# Plot again at new time range
fig2 = plt.figure(figsize=(10, 6))
ax1 = fig2.add_subplot(111)

# Plotting the traces with offset time
p1, = ax1.plot(fiber_time_offset, data.streams[Serotonin].data, linewidth=2, color='green', label='Serotonin')
p2, = ax1.plot(fiber_time_offset, data.streams[ISOS].data, linewidth=2, color='blueviolet', label='ISOS')

ax1.set_xlim(fiber_time_min, fiber_time_max)
ax1.axvline(x=180, color='red', linestyle='--', label='Shock')
ax1.set_ylabel('mV')
ax1.set_xlabel('Seconds')
ax1.set_title('Raw Demodulated Response with Artifact Removed')
ax1.legend(handles=[p1,p2], loc='upper right')
fig2.tight_layout()


# In[16]:


# Average around every Nth point and downsample Nx
N = 10 # Average every 10 samples into 1 value
F405 = []
F465 = []

for i in range(0, len(data.streams[Serotonin].data), N):
    F465.append(np.mean(data.streams[Serotonin].data[i:i+N-1]))
data.streams[Serotonin].data = F465

for i in range(0, len(data.streams[ISOS].data), N):
    F405.append(np.mean(data.streams[ISOS].data[i:i+N-1]))
data.streams[ISOS].data = F405

fiber_time = fiber_time[::N]
fiber_time = fiber_time[:len(data.streams[Serotonin].data)]
fiber_time_offset = fiber_time + fiber_offset  # Recalculate offset time after downsampling

# dFF calculation
x = np.array(data.streams[ISOS].data)
y = np.array(data.streams[Serotonin].data)
bls = np.polyfit(x, y, 1)
Y_fit_all = np.multiply(bls[0], x) + bls[1]
Y_dF_all = y - Y_fit_all
dFF = np.multiply(100, np.divide(Y_dF_all, Y_fit_all))
std_dFF = np.std(dFF)


# In[17]:


# Final dFF plot with offset time
fig3 = plt.figure(figsize=(20,12))
ax2 = fig3.add_subplot(311)

p1, = ax2.plot(fiber_time_offset, dFF, linewidth=2, color='green', label='Serotonin')
ax2.set_xlim(fiber_time_min, fiber_time_max)
ax2.axvline(x=180, color='red', linestyle='--', label='Shock')
ax2.set_ylabel(r'$\Delta$F/F')
ax2.set_xlabel('Seconds')
ax2.set_title('dFF')
ax2.legend(fontsize=12, markerscale=0.8, handlelength=1, handletextpad=0.5, labelspacing=0.5, loc='upper left')
fig3.tight_layout()


# In[18]:


# Final dFF plot with freezing highlights
fig3 = plt.figure(figsize=(20,12))
ax2 = fig3.add_subplot(311) 

# Plot dFF
p1, = ax2.plot(fiber_time_offset, dFF, linewidth=2, color='green', label='5HT Signal')

# Add freezing highlights using the same subplot configuration
ax2.fill_between(time_in_seconds, 
                 ax2.get_ylim()[0],  # Use the natural y-limits from the dFF plot
                 ax2.get_ylim()[1],
                 where=Freezing>0, 
                 color='gray', 
                 alpha=0.3)

# Add shock line and formatting - keeping everything identical to original
ax2.set_xlim(fiber_time_min, fiber_time_max)
ax2.axvline(x=180, color='red', linestyle='--', label='Shock')
ax2.set_ylabel(r'$\Delta$F/F')
ax2.set_xlabel('Seconds')
ax2.set_title('dFF with Freezing Highlighted in Gray')
ax2.legend(fontsize=12, markerscale=0.8, handlelength=1, handletextpad=0.5, labelspacing=0.5, loc='upper left')
fig3.tight_layout()


# In[ ]:




