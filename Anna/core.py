def time_to_seconds(time_str: str) -> float:
    """
    Convert time strings to seconds.

    Parameters:
    ----------
    time_str : str
        Time string in the format '%I:%M:%S%p'

    Returns:
    -------
    float
        Time in seconds.
    """
    t = datetime.strptime(time_str, "%I:%M:%S%p")
    return timedelta(hours=t.hour, minutes=t.minute, seconds=t.second).total_seconds()