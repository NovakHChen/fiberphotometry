"""
Routine to handle video files.
by: Gergely Turi
gt2253@cumc.columbia.edu 
"""
from dataclasses import dataclass
from os.path import join

from cv2 import (
    CAP_PROP_FPS,
    CAP_PROP_FRAME_COUNT,
    CAP_PROP_FRAME_HEIGHT,
    CAP_PROP_FRAME_WIDTH,
    CAP_PROP_POS_FRAMES,
    VideoCapture,
    VideoWriter,
    VideoWriter_fourcc,
)


@dataclass
class UsbVideo:
    """Video class to handle video files recored with USB camera."""

    vid_path: str

    def __post_init__(self):
        """Reads in all the data from tdt recording.
        f_path: str
            Path to the folder containing data."""
        self.video = VideoCapture(self.vid_path)

    @property
    def video_params(self) -> dict:
        """Returns the parameters of the recorded video."""
        params = {}
        cap = self.video
        if cap.isOpened():
            # get cap property
            params["width"] = cap.get(CAP_PROP_FRAME_WIDTH)  # float `width`
            params["height"] = cap.get(CAP_PROP_FRAME_HEIGHT)  # float `height`
            params["fps"] = cap.get(CAP_PROP_FPS)
            params["frame_count"] = cap.get(CAP_PROP_FRAME_COUNT)
        cap.release()
        return params

    def slice_video(self, start: int, end: int, codec: str) -> None:
        """Slices the video between start and end frames.
        Parameters:
        -----------
        start: int
            Start frame.
        end: int
            End frame.
        """
        cap = self.video
        save_path = self.vid_path.split(".")[0]

        # setup the video writer
        w_frame, h_frame = int(cap.get(CAP_PROP_FRAME_WIDTH)), int(
            cap.get(CAP_PROP_FRAME_HEIGHT)
        )
        fps = cap.get(CAP_PROP_FPS)
        cap.set(CAP_PROP_POS_FRAMES, start)
        fourcc = VideoWriter_fourcc(*codec)
        out = VideoWriter(
            join(save_path, "_sliced.avi"), fourcc, fps, (w_frame, h_frame)
        )
        counter = 0
        # read until the 'end'
        while cap.isOpened() and counter <= end:
            ret, frame = cap.read()
            counter += 1
            if ret:
                if counter >= start:
                    out.write(frame)
            else:
                break
        cap.release()
        out.release()
