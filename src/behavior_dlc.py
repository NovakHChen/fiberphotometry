"""Class for analyzing behavior data tracked with DeepLabCut
Maintainer: Gergely Turi
gt2253@cumc.columbia.edu"""


from dataclasses import dataclass
import numpy as np
import pandas as pd

@dataclass
class Behavior:
    """Class for analyzing behavior data tracked with DeepLabCut"""

    f_path: str
    
    def __post_init__(self):
        """Reads in the data from the hdf5 file."""
        self.data = pd.read_hdf(self.f_path)

    def pairwise_dist(self, coords: pd.Series) -> pd.Series:
        """Computes consecutive pairwise differences in a Series.

        NOTE: This is a helper function for distance_moved.

        Args:
            x_coords: pandas Series
                A one-dimensional ndarray of x coordinates, over time.

        Returns:
            dx: pandas Series
                A series containing all the values x[i] - x[i-1]

        """
        x_coords = coords.astype(float)
        delta_x = (np.roll(coords, -1) - x_coords).shift(1)
        return delta_x

    def distance_moved(self, x_coords: pd.Series,
                        y_coords: pd.Series) -> pd.Series:
        """Computes the distance moved per frame

        Args:
            x_coords: pandas Series
                A one-dimensional ndarray of x coordinates, over time.

            y_coords:
                A one-dimensional ndarray of y coordinates, over time.

        Returns
            Series containing distance moved per frame

        """
        if len(x_coords) != len(y_coords):
            raise ValueError("x_coords and y_coords are not of equal length!")
        if x_coords.empty or y_coords.empty:
            raise ValueError("x_coords and y_coords cannot be empty!")

        delta_x = self.pairwise_dist(x_coords.astype(float))
        delta_y = self.pairwise_dist(y_coords.astype(float))
        dist_moved = np.sqrt(delta_x**2 + delta_y**2)
        return dist_moved

    def compute_velocity(self, x_coords: pd.Series,
                        y_coords: pd.Series, framerate=10) -> pd.Series:
        """
        Args:
            framerate: int or float
                The frame rate of the video. Default is 10 fps.
            x_coords: pandas Series
                A one-dimensional ndarray of x coordinates of a body part.
            y_coords: pandas Series
                A one-dimensional ndarray of y coordinates of a body part.

        Returns:
            velocity: pandas Series
                A one-dimensional ndarray containing velocity in pixel/sec.
        """
        dist = self.distance_moved(x_coords, y_coords)
        time = 1 / framerate  # Calculate the time for one frame
        velocity = dist / time        
        return velocity

    def define_immobility(self, x_coords: pd.Series, y_coords: pd.Series,
                           framerate=10, min_dur=1, min_vel=2,
                            min_periods=1):
        """Define time periods of immobility based on a rolling window of velocity.

        A Mouse is considered immobile if velocity has not exceeded min_vel for the
        previous min_dur seconds.

        Default values for min_dur and min_vel are taken from:
        Stefanini...Fusi et al. 2018 (https://doi.org/10.1101/292953)

        Args:
            framerate: int or float
                The frame rate of the velocity Series. Default is 10 fps.

            min_dur: int, optional, default: 1
                The minimum length of time in seconds in which velocity must be low.

            min_vel: int, optional, default: 2
                The minimum velocity in cm/s for which the mouse can be considered
                mobile.

            min_periods: int, optional, default: 1
                Minimum number of datapoints needed to determine immobility. This
                value is needed to define immobile time bins at the beginning of the
                session. If min_periods=8, then the first 8 time bins will be be
                considered immobile, regardless of velocity.

        Returns:
            mobile_immobile: pandas Series
                A one-dimensional ndarray of 0's and 1's, where 1 signifies immobile
                times and 0 signifies mobile times.

        """
        window_size = framerate * min_dur
        velo = self.compute_velocity(x_coords, y_coords, framerate)
        rolling_max_vel = velo.rolling(window_size,
                                        min_periods=min_periods).max()
        mobile_immobile = (rolling_max_vel < min_vel).astype(int)

        return mobile_immobile