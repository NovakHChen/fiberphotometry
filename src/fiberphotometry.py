"""Dataclass for analyzing fiber photometry data.
This class is based on [FiberFlow](https://github.com/MicTott/FiberFlow)
maintainer: @gergelyturi"""

from dataclasses import dataclass
from typing import Tuple

import numpy as np
from scipy.signal import butter, filtfilt, medfilt
from scipy.stats import linregress
from tdt import read_block
from enum import Enum


class Channels(Enum):
    DYNAMIC = "_465A"
    ISOS = "_405A"


@dataclass
class ImportTDTData:
    """Class for reading TDT tank data.

    Example:
    >>> tdt_tank = fp(tank_path="path/to/tank")
    >>> fiberphotometry_data = tdt_tank.data
    """

    tank_path: str  # path to TDT tank

    DYNAMIC_CHANNEL: str = Channels.DYNAMIC.value
    ISOS_CHANNEL: str = Channels.ISOS.value

    def __post_init__(self):
        try:
            self.data = read_block(self.tank_path)
        except Exception as e:
            raise RuntimeError(f"Error reading TDT tank: {e}")

    @property
    def sampling_frequency(self) -> float:
        """Sampling frequency of the data."""
        return self.data.streams[self.DYNAMIC_CHANNEL].fs

    def load_data(self, channel: str) -> np.array:
        """Loads raw data for the specified channel."""
        try:
            return self.data.streams[channel].data
        except KeyError:
            raise ValueError(f"Channel {channel} not found in data.")


class SignalPreprocessor:
    """Class for preprocessing signals from fiber photometry data."""

    @staticmethod
    def preprocess(
        raw_data: np.array, sampling_frequency: float
    ) -> Tuple[np.array, np.array]:
        """Denoises signal with a median and lowpass filter, then subtracts a 4th order polynomial fit from the data."""
        # Median and lowpass filter with filtfilt
        median_filter = medfilt(raw_data, kernel_size=5)

        b, a = butter(2, 10, btype="low", fs=sampling_frequency)
        denoised = filtfilt(b, a, median_filter)

        # Fit 4th order polynomial to GCaMP signal and subtract
        coefs = np.polyfit(
            np.linspace(0, len(raw_data), num=len(raw_data)), denoised, deg=4
        )
        polyfit_data = np.polyval(
            coefs, np.linspace(0, len(raw_data), num=len(raw_data))
        )

        debleached = denoised - polyfit_data

        return debleached, denoised


class MotionCorrector:
    """Class for correcting motion artifacts in fiber photometry data."""

    @staticmethod
    def correct_motion(signal_prepro: np.array, isos_prepro: np.array) -> np.array:
        """Corrects motion by finding the linear fit between preprocessed signal and isosbestic signals."""
        # Find linear fit
        slope, intercept, _, _, _ = linregress(x=isos_prepro, y=signal_prepro)

        # Estimate motion correction and subtract
        est_motion = intercept + slope * isos_prepro
        motion_corrected = signal_prepro - est_motion

        return motion_corrected


class DeltaFoFCalculator:
    """Class for calculating dF/F from fiber photometry data."""

    @staticmethod
    def calculate_dfof(
        motion_corrected: np.array, denoised: np.array, sampling_frequency: float
    ) -> np.array:
        """Calculates the dF/F using the denoised data and the motion corrected signal."""
        b, a = butter(2, 0.001, btype="low", fs=sampling_frequency)
        baseline_fluorescence = filtfilt(b, a, denoised, padtype="even")

        dF_F = motion_corrected / baseline_fluorescence

        return dF_F


@dataclass
class FiberPhotometryAnalysis:
    """Class for running the complete fiber photometry analysis."""

    tank_path: str

    def __post_init__(self):
        self.photometry = ImportTDTData(tank_path=self.tank_path)

    def calculate_deltaf_f(self, strategy: str = "default") -> np.array:
        """Calculates the dF/F signal from the raw data using the specified strategy."""
        # Load data
        dynamic_data = self.photometry.load_data(self.photometry.DYNAMIC_CHANNEL.value)
        isos_data = self.photometry.load_data(self.photometry.ISOS_CHANNEL.value)

        if strategy == "default":
            # Preprocess signals
            signal_prepro, signal_denoised = SignalPreprocessor.preprocess(
                dynamic_data, self.photometry.sampling_frequency
            )
            isos_prepro, _ = SignalPreprocessor.preprocess(
                isos_data, self.photometry.sampling_frequency
            )

            # Correct motion
            signal_corrected = MotionCorrector.correct_motion(
                signal_prepro, isos_prepro
            )

            # Calculate dF/F
            signal_dF_F = DeltaFoFCalculator.calculate_dfof(
                signal_corrected, signal_denoised, self.photometry.sampling_frequency
            )
        elif strategy == "tdt":
            signal_dF_F = DeltaFoFStrategies.dfof_tdt(self.photometry.data)
        else:
            raise ValueError(f"Unknown strategy: {strategy}")

        return signal_dF_F


class DeltaFoFStrategies:
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
        x = f_data["streams"][Channels.ISOS.value].data  # isos
        y = f_data["streams"][Channels.DYNAMIC.value].data  # GCaMP

        bls = np.polyfit(x, y, 1)

        Y_fit_all = bls[0] * y + bls[1] if bls[0] >= 0 else np.mean(y)
        Y_dF_all = y - Y_fit_all

        dF_F = 100 * (Y_dF_all / Y_fit_all)
        return dF_F
