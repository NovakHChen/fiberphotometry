"""
This script extracts data from long recordings and processes fiber photometry data.
Functions:
- calculate_recording_start_times(recording_start_datetime, onsets):
- format_datetime_for_filename(dt):
- create_output_folder(data_dir, overwrite=False, alternative_name=None):
Main Execution:
- Parses command line arguments for data directory, overwrite option, and alternative folder name.
- Validates the existence and non-emptiness of the data directory.
- Creates the output folder.
- Imports TDT data and extracts onset and offset times.
- Calculates recording start times.
- Iterates over onsets and offsets to process and save fiber photometry data segments.

created by: Gergely Turi 11/29/2024
TODO: fix file names, it seems that the way how the datetime is increased is not working properly.
"""

import argparse as ap
import os
import shutil
import sys
from datetime import timedelta
from os.path import isdir, join

import pandas as pd

import src.fiberphotometry as fp
import src.logging_module as lm


def calculate_recording_start_times(recording_start_datetime, onsets):
    """
    Calculate a list of cumulative recording start times.

    Parameters:
    - recording_start_datetime: datetime.datetime
        The start date and time as a datetime object.
    - onsets: list or array-like
        The list of onset times in seconds.

    Returns:
    - list of datetime objects representing the start times.
    """
    # Initialize the `recording_start_times` list
    recording_start_times = []

    # Set the initial recording time
    current_time = recording_start_datetime + timedelta(seconds=float(onsets[0]))
    recording_start_times.append(current_time)

    # Iterate over the remaining onsets to add cumulative times
    for onset in onsets[1:]:
        current_time += timedelta(seconds=float(onset))
        recording_start_times.append(current_time)

    return recording_start_times


def format_datetime_for_filename(dt):
    """
    Format a datetime object into a string suitable for use in a filename.

    Parameters:
    - dt: datetime.datetime
        The datetime object to format.

    Returns:
    - str: A string formatted for use in a filename.
    """
    return dt.strftime("%Y%m%d_%H%M%S")


def create_output_folder(data_dir, overwrite=False, alternative_name=None):
    """
    Create an output folder named "analysis" inside the given data directory.

    Parameters:
    - data_dir: str
        The directory containing the data.
    - overwrite: bool
        Whether to overwrite the existing "analysis" folder if it exists.
    - alternative_name: str or None
        An alternative name for the output folder if "analysis" already exists.

    Returns:
    - str: The path to the output folder.
    """
    output_folder = join(data_dir, "analysis")

    if isdir(output_folder):
        if overwrite:
            lm.log_info("Overwriting existing 'analysis' folder.")
            shutil.rmtree(output_folder)
            os.makedirs(output_folder)
        elif alternative_name:
            output_folder = join(data_dir, alternative_name)
            lm.log_info(f"Creating alternative folder '{alternative_name}'.")
            os.makedirs(output_folder, exist_ok=True)
        else:
            lm.log_error(
                "The 'analysis' folder already exists. Use '--overwrite' or specify an alternative folder name."
            )
            sys.exit(1)
    else:
        lm.log_info(f"Creating output folder '{output_folder}'.")
        os.makedirs(output_folder)

    return output_folder


if __name__ == "__main__":
    # Setup logging
    lm.setup_logging()

    # Parse the command line arguments
    parser = ap.ArgumentParser(description="Extract data from long recordings.")
    parser.add_argument("data_dir", type=str, help="The directory containing the data.")
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite the existing 'analysis' folder if it exists.",
    )
    parser.add_argument(
        "--alt_folder",
        type=str,
        help="Alternative name for the analysis folder if 'analysis' already exists.",
        default=None,
    )
    args = parser.parse_args()

    # Set the data path and create the output folder
    data_path = args.data_dir
    if not isdir(data_path):
        lm.log_error(
            f"The data directory '{data_path}' does not exist or is not a directory."
        )
        sys.exit(1)
    if not os.listdir(data_path):
        lm.log_error(f"The data directory '{data_path}' is empty.")
        sys.exit(1)

    # Set the data path and create the output folder
    save_dir = create_output_folder(
        data_path, overwrite=args.overwrite, alternative_name=args.alt_folder
    )
    onset_add_time = float(10)  # seconds to add onset time to get rid of the artifact

    # Import data recording epocs and extract onset and offset times
    lm.log_info("Importing recording epocs.")
    recording_epocs = fp.ImportTDTData(
        tank_path=data_path, kwargs={"evtype": ["epocs"]}
    )

    onsets = recording_epocs.data.epocs.TC1_.onset
    offsets = recording_epocs.data.epocs.TC1_.offset
    on_off_times = {
        "onsets": onsets,
        "offsets": offsets,
    }

    recording_start_date_time = recording_epocs.data.info.start_date

    # Calculate recording start times
    lm.log_info("Calculating recording start times.")
    recording_starts = calculate_recording_start_times(
        recording_start_date_time, on_off_times["onsets"]
    )

    # Iterate through each onset and offset to extract data
    for on, off, start in zip(
        on_off_times["onsets"], on_off_times["offsets"], recording_starts
    ):
        adjusted_on = on + onset_add_time
        data_segment = fp.ImportTDTData(
            data_path,
            kwargs={
                "t1": float(adjusted_on),
                "t2": float(off),
            },
        )
        raw_ISO = data_segment.data.streams._405A.data
        raw_dynamic = data_segment.data.streams._465A.data

        processed_data = fp.FiberPhotometryAnalysis(
            data_path,
            kwargs={
                "t1": float(adjusted_on),
                "t2": float(off),
            },
        )

        dff = processed_data.calculate_deltaf_f()

        # Save the data
        save_name = f"fiber_data_{format_datetime_for_filename(start)}_{on}_{off}.csv"
        lm.log_info(f"Saving data to {save_name}.")
        data_to_save = {
            "raw_405nm": raw_ISO,
            "raw_465nm": raw_dynamic,
            "dff": dff,
        }

        data_to_save_df = pd.DataFrame.from_dict(data_to_save)
        data_to_save_df.to_csv(join(save_dir, save_name), index=False)
        lm.log_info(f"Data {save_name} is saved.")
