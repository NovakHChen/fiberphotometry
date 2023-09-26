# scripts for fiber photometry recordings.
# GT 2021

from dataclasses import dataclass

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from tdt import read_block

matplotlib.rcParams["font.size"] = 18  # set font size for all figures

# from bokeh.plotting import figure, show
# from bokeh.io import push_notebook, output_notebook
# output_notebook()


@dataclass
class FiberPhotometry:
    """Class for analyzing fiber photometry data.
    Initialize with the path to the TDT tank.
    Example:
    >>> tdt_tank = fp(tank_path="path/to/tank")
    >>> fp_data = tdt_tank.data"""

    tank_path: str
    # global variables
    GCAMP = "_465A"  # GCaMP channel (dynamic signal)
    ISOS = "_405A"  # Isobestic channel (static signal)

    def __post_init__(self):
        self.data = read_block(self.tank_path)
        self.GCAMP = "_465A"  # GCaMP channel (dynamic signal)
        self.ISOS = "_405A"

    def resample(self):
        """making a time array based on the number of samples
        and the sample frequency sampling

        Parameters:
        -----------
        data : tdt block"""
        data = self.data
        npts = len(data.streams[self.GCAMP].data)
        time_x = np.linspace(1, npts, npts) / data.streams[self.GCAMP].fs

        return time_x

    def downsampling(self, data, N=10):
        """downsampling the data

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

        decimated_GCAMP = []
        decimated_ISOS = []

        for i in range(0, len(self.data.streams[GCAMP].data), N):
            # This is the moving window mean
            decimated_GCAMP.append(
                np.mean(np.asarray(data.streams[GCAMP].data[i : i + N - 1]))
            )
        data.streams[GCAMP].data = np.asarray(decimated_GCAMP)

        for i in range(0, len(self.data.streams[ISOS].data), N):
            # This is the moving window mean
            decimated_ISOS.append(
                np.mean(np.asarray(data.streams[ISOS].data[i : i + N - 1]))
            )
        data.streams[ISOS].data = np.asarray(decimated_ISOS)

        time_x = (
            np.linspace(
                1,
                len(data.streams[GCAMP].data),
                len(data.streams[GCAMP].data),
            )
            / data.streams[GCAMP].fs
        )
        # time_x = resample(data)
        # time_x = time_x[::N] # go from beginning to end of array in steps on N
        # time_x = time_x[:len(data.streams[GCAMP].data)]

        return data

    def artifact_removal(data):
        """There is often a large artifact on the onset
        of LEDs turning on. This function removes data below a set time t

        Parameters:
        -----------
        data : tdt block
        channel : global variable
            either GCAMP or ISOS
        """

        t = 8
        time_x = resample(data)

        inds = np.where(time_x > t)
        ind = inds[0][0]
        time_x = time_x[ind:]  # go from ind to final index

        data.streams[GCAMP].data = np.asarray(data.streams[GCAMP].data[ind:])
        data.streams[ISOS].data = np.asarray(data.streams[ISOS].data[ind:])

        return data

    def detrending(data, time=False):
        """Full trace dFF according to Lerner et al. 2015
        dFF using 405 fit as baseline
        """
        x = np.array(data.streams[ISOS].data)
        y = np.array(data.streams[GCAMP].data)
        bls = np.polyfit(x, y, 1)
        Y_fit_all = np.multiply(bls[0], x) + bls[1]
        Y_dF_all = y - Y_fit_all

        dFF = np.multiply(100, np.divide(Y_dF_all, Y_fit_all))
        std_dFF = np.std(dFF)

        npts = len(dFF)
        time_x = np.linspace(1, npts, npts) / data.streams[GCAMP].fs

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
    
    x1 and x2 are the two channels of data (465 and 405)
  """

    def plotting(data, ax=None, kind="raw"):
        """plotting the fiberphotometry traces

        Parameters:
        -----------
        data: tdt data
        kind: string
            'raw' - raw data as it was recorded
            'rawDemod' - raw demodulated data, with artifact removal
            'dfof' - delta F over F plot
        ax : axes object (optional)
        N : int
            number of points for averaging

        """

        if ax is None:
            ax = plt.gca()

        if kind == "raw":
            time_x = resample(data)
            (p1,) = ax.plot(
                time_x,
                np.asarray(data.streams[GCAMP].data),
                linewidth=0.2,
                color="green",
                label="GCaMP",
            )
            (p2,) = ax.plot(
                time_x,
                np.asarray(data.streams[ISOS].data),
                linewidth=0.2,
                color="blueviolet",
                label="ISOS",
            )
            ax.set_title("Raw Demodulated Responses")
            ax.set_ylabel("mV")
            ax.set_xlabel("Seconds")
            ax.set_title("raw photometry traces")
            ax.legend(handles=[p1, p2], loc="upper right")

        elif kind == "rawDemod":
            data = artifact_removal(data)
            time_x = resample(data)
            (p1,) = ax.plot(
                time_x,
                np.asarray(data.streams[GCAMP].data),
                linewidth=0.2,
                color="green",
                label="GCaMP",
            )
            (p2,) = ax.plot(
                time_x,
                np.asarray(data.streams[ISOS].data),
                linewidth=0.2,
                color="blueviolet",
                label="ISOS",
            )
            ax.set_ylabel("mV")
            ax.set_xlabel("Seconds")
            ax.set_title("Demodulated photometry traces")
            ax.legend(handles=[p1, p2], loc="upper right")

        elif kind == "dfof":
            dFF, time_x = detrending(data, time=True)
            (p1,) = ax.plot(
                time_x, np.array(dFF), linewidth=0.2, color="green", label="GCaMP"
            )
            ax.set_ylabel(r"$\Delta$F/F")
            ax.set_xlabel("Seconds")
            ax.legend(handles=[p1], loc="upper right")
            ax.set_title("dFoF")

        return ax
