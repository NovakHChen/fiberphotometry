# scripts for fiber photometry recordings. 
# GT 2021

from dataclasses import dataclass
from tdt import read_block

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import zscore
from scipy.signal import decimate
import pandas as pd

matplotlib.rcParams['font.size'] = 18 # set font size for all figures

# from bokeh.plotting import figure, show
# from bokeh.io import push_notebook, output_notebook
# output_notebook()


@dataclass
class FiberPhotometry:
    """Class for analyzing fiber photometry data."""

    tank_path: str
    # global variables
    GCAMP = '_465A' # GCaMP channel (dynamic signal) 
    ISOS = '_405A' # Isobestic channel (static signal)
    
    def __post_init__(self):
        photometry_data = read_block(self.tank_path)
    
    def resample(self):
        """making a time array based on the number of samples 
        and the sample frequency sampling
        
        Parameters:
        -----------
        photometry_data : tdt block"""
        
        npts = len(self.photometry_data.streams[GCAMP].photometry_data)
        time_x = np.linspace(1, npts, npts) / photometry_data.streams[GCAMP].fs
        
        return time_x

    def downsampling(self, photometry_data, N=10):
        """downsampling the photometry_data 
        
        Parameters:
        -----------
        photometry_data : tdt block
        channel : global variable
            either GCAMP or ISOS
        N : int
            number of points for averaging
            
        Returns:
        --------
        dictionary of numpy arrays with the decimated signal and time 
        """
        
        decimated_GCAMP = []
        decimated_ISOS = []
                
        for i in range(0, len(self.photometry_data.streams[GCAMP].photometry_data), N):        
            # This is the moving window mean
            decimated_GCAMP.append(np.mean(np.asarray(photometry_data.streams[GCAMP].photometry_data[i:i+N-1])))
        photometry_data.streams[GCAMP].photometry_data = np.asarray(decimated_GCAMP)
        
        for i in range(0, len(self.photometry_data.streams[ISOS].photometry_data), N):        
            # This is the moving window mean
            decimated_ISOS.append(np.mean(np.asarray(photometry_data.streams[ISOS].photometry_data[i:i+N-1])))
        photometry_data.streams[ISOS].photometry_data = np.asarray(decimated_ISOS)

        time_x = np.linspace(1,len(photometry_data.streams[GCAMP].photometry_data),
        len(photometry_data.streams[GCAMP].photometry_data))/photometry_data.streams[GCAMP].fs
        # time_x = resample(photometry_data)
        # time_x = time_x[::N] # go from beginning to end of array in steps on N
        # time_x = time_x[:len(photometry_data.streams[GCAMP].photometry_data)]
            
        return photometry_data

    def artifact_removal(photometry_data):
        """There is often a large artifact on the onset
        of LEDs turning on. This function removes photometry_data below a set time t
        
        Parameters:
        -----------
        photometry_data : tdt block
        channel : global variable
            either GCAMP or ISOS
        """
        
        
        t = 8
        time_x = resample(photometry_data)
        
        inds = np.where(time_x > t)
        ind = inds[0][0]
        time_x = time_x[ind:] # go from ind to final index
        
        photometry_data.streams[GCAMP].photometry_data = np.asarray(photometry_data.streams[GCAMP].photometry_data[ind:])
        photometry_data.streams[ISOS].photometry_data = np.asarray(photometry_data.streams[ISOS].photometry_data[ind:])
            
        return photometry_data
    
        
    def detrending(photometry_data, time=False):
        """Full trace dFF according to Lerner et al. 2015
        dFF using 405 fit as baseline
        """
        x = np.array(photometry_data.streams[ISOS].photometry_data)
        y = np.array(photometry_data.streams[GCAMP].photometry_data)
        bls = np.polyfit(x, y, 1)
        Y_fit_all = np.multiply(bls[0], x) + bls[1]
        Y_dF_all = y - Y_fit_all

        dFF = np.multiply(100, np.divide(Y_dF_all, Y_fit_all))
        std_dFF = np.std(dFF)

        npts = len(dFF)
        time_x = np.linspace(1, npts, npts) / photometry_data.streams[GCAMP].fs
        
        if time:
            return dFF, time_x
        else:
            return dFF
    # TODO: add a function to calculate dFF based on this.
    """
    YP's matlab code for dfof calculation
    x1=photData(1).data;
    x2=photData(2).data;
    reg = polyfit(x2,x1,1);
    disp(reg)
    if reg(1)<0
        f0=mean(x1);
    else
        f0=reg(1).*x2+reg(2);
    end
    delF=100.*(x1-f0)./f0;
    
    x1 and x2 are the two channels of photometry_data (465 and 405)
  """
    
        
    def plotting(photometry_data, ax=None, kind='raw'):
        """ plotting the fiberphotometry traces
        
        Parameters:
        -----------
        photometry_data: tdt photometry_data
        kind: string
            'raw' - raw photometry_data as it was recorded
            'rawDemod' - raw demodulated photometry_data, with artifact removal
            'dfof' - delta F over F plot
        ax : axes object (optional)
        N : int
            number of points for averaging 
        
        """
        
        if ax is None:
            ax=plt.gca()
                
        if (kind=='raw'):
            time_x = resample(photometry_data)
            p1, = ax.plot(time_x, np.asarray(photometry_data.streams[GCAMP].photometry_data),
            linewidth=.2, color='green', label='GCaMP')
            p2, = ax.plot(time_x, np.asarray(photometry_data.streams[ISOS].photometry_data),
            linewidth=.2, color='blueviolet', label='ISOS')
            ax.set_title('Raw Demodulated Responses')
            ax.set_ylabel('mV')
            ax.set_xlabel('Seconds')
            ax.set_title('raw photometry traces')
            ax.legend(handles=[p1,p2], loc='upper right')
        
        elif (kind=='rawDemod'):
            photometry_data = artifact_removal(photometry_data)
            time_x = resample(photometry_data)
            p1, = ax.plot(time_x, np.asarray(photometry_data.streams[GCAMP].photometry_data),
            linewidth=.2, color='green', label='GCaMP')
            p2, = ax.plot(time_x, np.asarray(photometry_data.streams[ISOS].photometry_data),
            linewidth=.2, color='blueviolet', label='ISOS')    
            ax.set_ylabel('mV')
            ax.set_xlabel('Seconds')
            ax.set_title('Demodulated photometry traces')
            ax.legend(handles=[p1,p2], loc='upper right')
        
        elif (kind=='dfof'):                    
            dFF, time_x = detrending(photometry_data, time=True)        
            p1, = ax.plot(time_x, np.array(dFF), linewidth=.2,
                color='green', label='GCaMP')
            ax.set_ylabel(r'$\Delta$F/F')
            ax.set_xlabel('Seconds')
            ax.legend(handles=[p1], loc='upper right')
            ax.set_title('dFoF')

        return ax    