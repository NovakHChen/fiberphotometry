"""Data class for TDT experiment."""

import os
from dataclasses import dataclass
from datetime import datetime
from os.path import join
from typing import Optional


@dataclass
class TDTExperiment:
    """
    A dataclass representing a TDT experiment, holding references to key directory paths.

    Attributes
    ----------
    exp_path : str, optional
        The base path to the experiment directory. If None, properties that depend on exp_path
        may fail or return None, depending on implementation.
    """

    exp_path: Optional[str] = None

    def __post_init__(self):
        """
        Validate the experiment path after initialization.
        """
        if self.exp_path is not None:
            if not os.path.isdir(self.exp_path):
                raise ValueError(
                    f"Provided experiment path does not exist or is not a directory: {self.exp_path}"
                )

    def _check_exp_path_set(self):
        """Helper to ensure exp_path is set."""
        if self.exp_path is None:
            raise ValueError(
                "exp_path must be set before accessing experiment resources."
            )

    def _get_dir_path(self, dirname: str) -> str:
        """
        Helper to construct and validate a directory path.

        Parameters
        ----------
        dirname : str
            Name of the subdirectory within exp_path.

        Returns
        -------
        str
            Full path to the directory.

        Raises
        ------
        FileNotFoundError
            If the directory doesn't exist.
        """
        self._check_exp_path_set()
        path = join(self.exp_path, dirname)
        if not os.path.isdir(path):
            raise FileNotFoundError(f"Directory does not exist: {path}")
        return path

    def _read_file_contents(self, filename: str) -> str:
        """
        Helper to read the contents of a file in exp_path.

        Parameters
        ----------
        filename : str
            The filename to read.

        Returns
        -------
        str
            Contents of the file.

        Raises
        ------
        FileNotFoundError
            If the file does not exist.
        """
        self._check_exp_path_set()
        path = join(self.exp_path, filename)
        if not os.path.isfile(path):
            raise FileNotFoundError(f"File does not exist: {path}")
        with open(path, "r") as f:
            return f.read()

    def _get_line_value(self, prefix: str) -> str:
        """
        Helper method to extract the value following a given prefix in the Notes file.

        Parameters
        ----------
        prefix : str
            The prefix to look for (e.g., "Experiment:", "Subject:")

        Returns
        -------
        str
            The string value after the prefix.

        Raises
        ------
        ValueError
            If no line with the given prefix is found.
        """
        lines = self.notes.splitlines()
        for line in lines:
            if line.startswith(prefix):
                # Example line: "Experiment: pattern"
                # split by ": ", maxsplit=1 to separate prefix from the remaining value
                parts = line.split(": ", 1)
                if len(parts) > 1:
                    return parts[1].strip()
                else:
                    # If the line has the prefix but nothing after, return an empty string or raise an error
                    return ""

        raise ValueError(f"No line starting with {prefix} found in Notes.txt")

    @property
    def analysis_path(self) -> str:
        """
        Returns the path to the 'analyzed_data' directory within the experiment path.
        """
        return self._get_dir_path("analyzed_data")

    @property
    def stores_listings(self) -> str:
        """
        Returns the content of the `StoresListing.txt` file.
        """
        return self._read_file_contents("StoresListing.txt")

    @property
    def notes(self) -> str:
        """
        Returns the content of the `Notes.txt` file.
        """
        return self._read_file_contents("Notes.txt")

    @property
    def experiment_name(self) -> str:
        """
        Returns the experiment name defined after "Experiment:" in Notes.txt
        """
        return self._get_line_value("Experiment:")

    @property
    def subject_name(self) -> str:
        """
        Returns the subject name defined after "Subject:" in Notes.txt
        """
        return self._get_line_value("Subject:")

    def experiment_start_stop(self):
        """
        Returns:
            tuple: (start_datetime, stop_datetime) as datetime objects of the experiment start and stop times.
        """

        # Get the notes content
        notes_content = self.notes.splitlines()

        # Extract the start and stop lines
        # We'll find lines that start with 'Start:' or 'Stop:'
        # Example line: "Start: 3:27:29pm 06/11/2024"
        start_line = None
        stop_line = None

        for line in notes_content:
            if line.startswith("Start:"):
                # Split by ': ' once to separate the label from the datetime string
                start_line = line.split(": ", 1)[1]
            elif line.startswith("Stop:"):
                stop_line = line.split(": ", 1)[1]

        if start_line is None or stop_line is None:
            raise ValueError("Could not find valid Start or Stop lines in Notes.txt")

        # Parse the datetime strings using the appropriate format
        start_dt = datetime.strptime(start_line, "%I:%M:%S%p %m/%d/%Y")
        stop_dt = datetime.strptime(stop_line, "%I:%M:%S%p %m/%d/%Y")

        return start_dt, stop_dt
