# scripts for fiber photometry recordings. 
# GT 2021

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import zscore
import pandas as pd
from tdt import read_block, read_sev, epoc_filter 
matplotlib.rcParams['font.size'] = 18 # set font size for all figures

# from bokeh.plotting import figure, show
# from bokeh.io import push_notebook, output_notebook
# output_notebook()

# global variables
GCAMP = '_465N' # GCaMP channel (dynamic signal) 
ISOS = '_405N' # Isobestic channel (static signal)

def resample(data):
    """making a time array based on the number of samples 
    and the sample frequency sampling
    
    Parameters:
    -----------
    data : tdt block"""
    
    npts = len(data.streams[GCAMP].data)
    time_x = np.linspace(1, npts, npts) / data.streams[GCAMP].fs
    
    return time_x

def downsampling(data, channel, N=10):
    """downsampling the data for plottig
    
    Parameters:
    -----------
    data : tdt block
    channel : global variable
        either GCAMP or ISOS
    N : int
        number of points for averaging
        
    Returns:
    --------
    dictionary of numpy arrays with the decimated signal and time 
    """
    decimatedData = {}
    decimatedSignal = []
    decimatedTime = []
            
    for i in range(0, len(data.streams[channel].data), N):        
        # This is the moving window mean
        mean_wnd = np.mean(data.streams[channel].data[i:i+N-1])
        decimatedSignal.append(mean_wnd)
    np.array(decimatedSignal)
    
    time_x = resample(data)
    time_x = time_x[::N] # go from beginning to end of array in steps on N
    time_x = time_x[:len(data.streams[channel].data)]
    
    decimatedData['decimatedSignal'] = decimatedSignal
    decimatedData['decimatedTime'] = time_x
    
    return decimatedData  

def artifactRemoval(data):
    """Artifact Removal There is often a large artifact on the onset
       of LEDs turning on Remove data below a set time t
       
    Parameters:
    -----------
    data : tdt block
    channel : global variable
        either GCAMP or ISOS
     """
    noArtifactData = {}
    noArtifactGAMP = []
    noArtifactISOS = []
    t = 8
    time_x = resample(data)
    
    inds = np.where(time_x > t)
    ind = inds[0][0]
    time_x = time_x[ind:] # go from ind to final index
    
    noArtifactData['GCAMP'] = data.streams[GCAMP].data[ind:]
    noArtifactData['ISOS'] = data.streams[ISOS].data[ind:]
    noArtifactData['TIME'] = time_x
    
    return noArtifactData
  
    
def detrending(data):
    """Full trace dFF according to Lerner et al. 2015
       dFF using 405 fit as baseline
    """
    x = artifactRemoval(data)['ISOS']
    y = artifactRemoval(data)['GCAMP']
    bls = np.polyfit(x, y, 1)
    Y_fit_all = np.multiply(bls[0], x) + bls[1]
    Y_dF_all = y - Y_fit_all

    dFF = np.multiply(100, np.divide(Y_dF_all, Y_fit_all))
    std_dFF = np.std(dFF)
    
    return dFF
    
    
    
def plotting(data, kind='raw'):
    """ plotting the fiberphotometry traces
    
    Parameters:
    -----------
    data: tdt data
    kind: string
        'raw' - raw data as it was recorded
        'rawDemod' - raw demodulated data, with artifact removal
        'dfof' - delta F over F plot
     
    """
    # creating the x (time) axis
    time_x = resample(data)
    
    fig = plt.figure(figsize=(10,6))
    ax0 = fig.add_subplot(111)
    
    if (kind=='raw'):
        p1, = ax0.plot(time_x, data.streams[GCAMP].data, linewidth=2,
                       color='green', label='GCaMP')
        p2, = ax0.plot(time_x, data.streams[ISOS].data, linewidth=2,
                       color='blueviolet', label='ISOS')
        ax0.set_title('Raw Demodulated Responses')
        ax0.set_ylabel('mV')
        ax0.set_xlabel('Seconds')
        ax0.set_title('raw photometry traces')
        ax0.legend(handles=[p1,p2], loc='upper right')
     
    elif (kind=='rawDemod'):
        data = artifactRemoval(data)
        p1, = ax0.plot(data['TIME'], data['GCAMP'], linewidth=2,
               color='green', label='GCaMP')
        p2, = ax0.plot(data['TIME'], data['ISOS'], linewidth=2,
               color='blueviolet', label='ISOS')    
        ax0.set_ylabel('mV')
        ax0.set_xlabel('Seconds')
        ax0.set_title('Demodolated photometry traces')
        ax0.legend(handles=[p1,p2], loc='upper right')
    
    elif (kind=='dfof'):        
        dFF = detrending(data)
        p1, = ax0.plot(artifactRemoval(data)['TIME'], dFF, linewidth=2,
               color='green', label='GCaMP')
        ax0.set_ylabel(r'$\Delta$F/F')
        ax0.set_xlabel('Seconds')
        ax0.legend(handles=[p1], loc='upper right')
        ax0.set_title('dFoF')
    fig.tight_layout()    