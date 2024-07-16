"""Dataclass for analyzing fiber photometry data.
This class is based on [FiberFlow](https://github.com/MicTott/FiberFlow)
maintainer: @gergelyturi"""

from dataclasses import dataclass
from typing import Tuple

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

    DYNAMIC_CHANNEL: str = "_465A"  # e.g. GCaMP channel (dynamic signal)
    ISOS_CHANNEL: str = "_405A"  # Isobestic channel (static signal)

    def __post_init__(self):
        try:
            self.data = read_block(self.tank_path)
        except Exception as e:
            raise RuntimeError(f"Error reading TDT tank: {e}")

    def calculate_deltaf_f(self) -> np.array:
        """Calculates the dF/F signal from the raw data.

        Returns:
        --------
        np.array
            dF/F signal
        """
        # Preprocess
        signal_prepro, signal_denoised = self.preprocess(signal="dynamic")
        isos_prepro, _ = self.preprocess(self.ISOS_CHANNEL)

        # Correct motion
        signal_corrected = self.correct_motion(signal_prepro, isos_prepro)

        # Calculate dF/F
        signal_dF_F = self.deltaf_f(signal_corrected, signal_denoised)

        return signal_dF_F

    @property
    def sampling_frequency(self) -> float:
        """Sampling frequency of the data."""
        return self.data.streams[self.DYNAMIC_CHANNEL].fs

    def preprocess(self, channel: str) -> Tuple[np.array, np.array]:
        """Denoises signal with a median ad lowpass filter, then subtract
        a 4th order polyonmial fit from the data.

        Parameters:
        -----------
        channel: str
            Channel name, 'DYNAMIC_CHANNEL' or 'ISOS_CHANNEL'

        Returns:
        --------
        Tuple[np.ndarray, np.ndarray]
            Debleached and denoised signals
        """
        try:
            raw = self.data.streams[channel]
        except KeyError:
            raise ValueError(f"Channel {channel} not found in data.")

        # Median and lowpass filter with filtfilt
        median_filter = medfilt(raw.data, kernel_size=5)

        fs = self.sampling_frequency
        b, a = butter(2, 10, btype="low", fs=fs)
        denoised = filtfilt(b, a, median_filter)

        # Fit 4th order polynomial to GCaMP signal and subtract
        coefs = np.polyfit(
            np.linspace(0, len(raw.data), num=len(raw.data)), denoised, deg=4
        )
        polyfit_data = np.polyval(
            coefs, np.linspace(0, len(raw.data), num=len(raw.data))
        )

        debleached = denoised - polyfit_data

        return debleached, denoised

    def correct_motion(self, signal_prepro, isos_prepro) -> np.array:
        """Correct motion by finding the linear fit between preprocessed
        singal and isosbestic signals.

        Parameters:
        -----------
        signal_prepro: np.array
            Preprocessed signal signal (i.e. debleached)
        isos_prepro: np.array
            Preprocessed isos signal (i.e. debleached)

        Returns:
        --------
        motion_corrected: np.array
            Motion corrected signal
        """

        # find linear fit
        slope, intercept, r_value, p_value, std_err = linregress(
            x=isos_prepro, y=signal_prepro
        )

        # estimate motion correction and subtract
        est_motion = intercept + slope * isos_prepro
        motion_corrected = signal_prepro - est_motion

        return motion_corrected

    def deltaf_f(self, motion_corrected, denoised):
        """This function calculates the dF/F using the
        denoised data and the motion corrected.

        Parameters:
        -----------
        motion_corrected: np.array
            Motion corrected GCaMP signal
        denoised: np.array
            Denoised GCaMP signal

        Returns:
        --------
        dF_F: np.array
            dF/F signal
        """

        fs = self.sampling_frequency
        b, a = butter(2, 0.001, btype="low", fs=fs)
        baseline_fluorescence = filtfilt(b, a, denoised, padtype="even")

        dF_F = motion_corrected / baseline_fluorescence

        return dF_F


class DeltaFoFstrategies:
    """Class for various strategies of calculating dF/F from fiber photometry data."""

    @staticmethod
    def dfof_tdt(f_data):
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
