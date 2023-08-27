"""
Routine to handle video files.
by: Gergely Turi
gt2253@cumc.columbia.edu 
"""
from datetime import datetime

import tdt
from dataclasses import dataclass

@dataclass
class Video:
    """Video class to handle video files recored with USB camera. """
    def __init__(self, f_path):
        self.f_path = f_path
        self.data = tdt.read_block(self.f_path)

    def load_video_meta_data(self):
        """Loads video file and returns the data as numpy array."""
        return self.data['epocs']['Cam1']

    def recording_length(self):
        """Calculates frame rate based on the video meta data."""
        start = datetime.strptime(self.data['info']['start'],
                                   '%I:%M:%S%p %m/%d/%Y') 
        stop = datetime.strptime(self.data['info']['stop'],
                                  '%I:%M:%S%p %m/%d/%Y') 
        recording_lenght = stop - start
        return recording_lenght
    
    def frame_rate(self):
        """Calculates frame rate based on the video meta data."""
        recording_lenght = self.recording_length()
        frames = len(self.data['epocs']['Cam1']['data'])
        frame_rate = frames/recording_lenght.total_seconds()
        return frame_rate