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
    
    def frame_rate(self):
        """Calculates frame rate based on the video meta data."""
        recording_lenght = self.data.info['duration'].total_seconds()
        frames = len(self.data['epocs']['Cam1']['data'])
        frame_rate = frames/recording_lenght
        return frame_rate