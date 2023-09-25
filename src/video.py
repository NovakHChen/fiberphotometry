"""
Routine to handle video files.
by: Gergely Turi
gt2253@cumc.columbia.edu 
"""
from dataclasses import dataclass
import cv2

@dataclass
class UsbVideo:
    """Video class to handle video files recored with USB camera."""

    vid_path: str
    
    def __post_init__(self):
        """Reads in all the data from tdt recording. 
        f_path: str
            Path to the folder containing data."""
        self.video = cv2.VideoCapture(self.vid_path)

    @property
    def video_params(self) -> dict:
        """Returns the parameters of the recorded video.
        """
        params = {}
        vcap = self.video
        if vcap.isOpened(): 
        # get vcap property 
            params['width']  = vcap.get(cv2.CAP_PROP_FRAME_WIDTH)   # float `width`
            params['height'] = vcap.get(cv2.CAP_PROP_FRAME_HEIGHT)  # float `height`  
            params['fps'] = vcap.get(cv2.CAP_PROP_FPS)
        return params
