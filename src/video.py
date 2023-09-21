"""
Routine to handle video files.
by: Gergely Turi
gt2253@cumc.columbia.edu 
"""
from dataclasses import dataclass
import tdt


@dataclass
class Video:
    """Video class to handle video files recored with USB camera."""

    f_path: str
    
    def __post_init__(self):
        """Reads in the data from the hdf5 file."""
        self.data = tdt.read_block(self.f_path)

    def frame_rate(self, rounded=True) -> float or int:
        """Calculates frame rate based on the video meta data.
        Returns: int or float depending on the rounded parameter.
        """
        recording_lenght = self.data.info["duration"].total_seconds()
        frames = len(self.data["epocs"]["Cam1"]["data"])
        f_rate = frames / recording_lenght
        if rounded:
            fr_rate = round(f_rate)
        else:
            fr_rate = f_rate
        return fr_rate
