"""Dataclass for analyzing fiber photometry data.
This class is based on [FiberFlow](https://github.com/MicTott/FiberFlow)
maintainer: @gergelyturi"""

from dataclasses import dataclass

import numpy as np
from scipy.signal import butter, filtfilt, medfilt
from scipy.stats import linregress
from tdt import read_block


@dataclass
class FiberPhotometry:
    """Class for analyzing fiber photometry data.
    Initialize with the path to the TDT tank.
    Example:
    >>> tdt_tank = fp(tank_path="path/to/tank")
    >>> fiberphotometry_data = tdt_tank.data
    """

    tank_path: str  # path to TDT tank
    dynamic = str  # e.g. GCaMP channel (dynamic signal)
    isos = str  # Isobestic channel (static signal)

    def __post_init__(self):
        self.data = read_block(self.tank_path)
        self.dynamic = "_465A"  # GCaMP channel (dynamic signal)
        self.isos = "_405A"  # Isobestic channel (static signal)

    def calculate_deltaf_f(self) -> np.array:
        """This function calculates the dF/F signal
        from the raw data.

        Returns:
        --------
        GCaMP_dF_F: np.array
            dF/F signal
        """
        # Preprocess
        GCaMP_prepro, GCaMP_denoised = self.preprocess(signal="dynamic")
        ISOS_prepro, _ = self.preprocess(signal="isos")

        # Correct motion
        GCaMP_corrected = self.correct_motion(GCaMP_prepro, ISOS_prepro)

        # Calculate dF/F
        GCaMP_dF_F = self.deltaF_F(GCaMP_corrected, GCaMP_denoised)

        return GCaMP_dF_F

    @property
    def sampling_frequency(self):
        """Sampling frequency of the data."""
        return self.data.streams["_465A"].fs

    def preprocess(self, signal: str) -> np.array:
        """This function denoises GCaMP or isos signals
        with a median ad lowpass filter. Then it fits a 4th order
        polyonmial to the data subtracts the polyomial fit from the
        raw data.

        Parameters:
        -----------
        signal: str
            'dynamic' or 'isos'

        Returns:
        --------
        debleached: np.array
            Debleached signal
        denoised: np.array
            Denoised signal
        """
        if signal == "dynamic":
            raw = self.data.streams[self.dynamic]
        elif signal == "isos":
            raw = self.data.streams[self.isos]

        # Median and lowpass filter with filtfilt
        denoised_med = medfilt(raw.data, kernel_size=5)

        fs = self.sampling_frequency
        b, a = butter(2, 10, btype="low", fs=fs)
        denoised = filtfilt(b, a, denoised_med)

        # Fit 4th order polynomial to GCaMP signal and subtract
        coefs = np.polyfit(
            np.linspace(0, len(raw.data), num=len(raw.data)), denoised, deg=4
        )
        polyfit_data = np.polyval(
            coefs, np.linspace(0, len(raw.data), num=len(raw.data))
        )

        debleached = denoised - polyfit_data

        return debleached, denoised

    def correct_motion(self, GCaMP_prepro, ISOS_prepro) -> np.array:
        """This function takes preprocessed GCaMP and Isosbestic
        sigals and finds the linear fit, then estimates the
        motion correction and substracts it from GCaMP.

        Parameters:
        -----------
        GCaMP_prepro: np.array
            Preprocessed GCaMP signal
        ISOS_prepro: np.array
            Preprocessed isos signal

        Returns:
        --------
        GCaMP_corrected: np.array
            Motion corrected GCaMP signal
        """

        # find linear fit
        slope, intercept, r_value, p_value, std_err = linregress(
            x=ISOS_prepro, y=GCaMP_prepro
        )

        # estimate motion correction and subtract
        GCaMP_est_motion = intercept + slope * ISOS_prepro
        GCaMP_corrected = GCaMP_prepro - GCaMP_est_motion

        return GCaMP_corrected

    def deltaf_f(self, GCaMP_corrected, denoised):
        """This function calculates the dF/F using the
        denoised data and the motion corrected.

        Parameters:
        -----------
        GCaMP_corrected: np.array
            Motion corrected GCaMP signal
        denoised: np.array
            Denoised GCaMP signal

        Returns:
        --------
        GCaMP_dF_F: np.array
            dF/F signal
        """

        fs = self.sampling_frequency
        b, a = butter(2, 0.001, btype="low", fs=fs)
        baseline_fluorescence = filtfilt(b, a, denoised, padtype="even")

        GCaMP_dF_F = GCaMP_corrected / baseline_fluorescence

        return GCaMP_dF_F


class DeltaFoFstrategies:
    """Class for various strategies of calculating dF/F from fiber photometry data."""

    def dfof_tdt(self, f_data):
        """Calculate dF/F using the method in the TDT Offline Data Analysis workbook.
        based on Lerner et al. 2015
        https://dx.doi.org/10.1016/j.cell.2015.07.014

        Parameters:
        -----------
        f_data: TDT tank data
            Fiber photometry data

        Returns:
        --------
        dF_F: np.array
            dF/F signal
        """
        x = f_data["streams"]["_405A"].data[500:]  # isos
        y = f_data["streams"]["_465A"].data[500:]  # GCaMP

        bls = np.polyfit(x, y, 1)

        Y_fit_all = np.multiply(bls[0], x) + bls[1]
        Y_dF_all = y - Y_fit_all

        dF_F = np.multiply(100, np.divide(Y_dF_all, Y_fit_all))
        return dF_F
