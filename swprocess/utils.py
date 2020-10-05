"""Surface wave processing utilities."""

import os
import datetime
import logging
import warnings

import numpy as np
import obspy
import pandas as pd

logger = logging.getLogger("swprocess.utils")


def extract_mseed(startend_fname, network, data_dir="./", output_dir="./", extension="mseed"):
    """Extract specific time blocks from a set of miniseed files.

    Reads a large set of miniseed files, trims out specified time
    block(s), and writes the trimmed block(s) to disk. Useful for
    condensing a large dataset consisting of miniseed files written at
    the end of each hour to a single file that spans several hours.
    Stations which share an array name will appear in a common
    directory.

    Parameters
    ----------
    startend_fname : str
        Name of .xlsx or .csv file with start and end times. An example
        file is provided here TODO (jpv): Add link to example file.
    network : str
        Short string of characters to identify the network. Exported
        files will utilize this network code as its prefix.
    data_dir : str, optional
        The full or a relative file path to the directory containing the
        miniseed files, default is the current directory.
    output_dir : str, optional
        The full or a relative file path to the location to place the
        output miniseed files, default is the current directory.
    extension : {"mseed", "miniseed"}, optional
        Extension used for miniSEED format, default is `"mseed"`.

    Returns
    -------
    None
        Writes folder and files to disk.

    """
    # Read start and end times.
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            df = pd.read_excel(startend_fname)
    except:
        raise NotImplementedError("To implement .csv parsing")

    # Loop through across defined timeblocks.
    logger.info("Begin iteration across dataframe ...")
    total = df["folder"].count()
    for index, series in df.iterrows():
        logger.debug(f"\tindex={index} series={series}")

        # Start and end time.
        starttime = datetime.datetime(year=series["start year"],
                                      month=series["start month"],
                                      day=series["start date"],
                                      hour=series["start hour"],
                                      tzinfo=datetime.timezone.utc)
        logging.debug(f"\t\tstarttime={starttime}")
        currenttime = starttime

        endtime = datetime.datetime(year=series["end year"],
                                    month=series["end month"],
                                    day=series["end date"],
                                    hour=series["end hour"],
                                    tzinfo=datetime.timezone.utc)
        logging.debug(f"\t\tendtime={endtime}")

        # Avoid nonsensical time blocks.
        if endtime < starttime:
            msg = f"endtime={endtime} is less than starttime={starttime}."
            raise ValueError(msg)

        # Loop across the required hours and merge traces.
        append = False
        dt = datetime.timedelta(hours=1)
        while currenttime <= endtime:

            # miniSEED file name: NW.STNSN_SENSOR_YYYYMMDD_HH0000.miniseed
            fname = f"{network}.STN{str(series['station number']).zfill(2)}_{currenttime.year}{str(currenttime.month).zfill(2)}{str(currenttime.day).zfill(2)}_{str(currenttime.hour).zfill(2)}0000.{extension}"

            # Read current file and append if necessary
            if append:
                master += obspy.read(f"{data_dir}{fname}")
            else:
                master = obspy.read(f"{data_dir}{fname}")
                append = True

            currenttime += dt

        master = master.merge(method=1)

        # Trim merged traces between specified start and end times
        trim_start = obspy.UTCDateTime(series["start year"], series["start month"],
                                       series["start date"], series["start hour"],
                                       series["start minute"], series["start second"])
        trim_end = obspy.UTCDateTime(series["end year"], series["end month"],
                                     series["end date"], series["end hour"],
                                     series["end minute"], series["end second"])
        master.trim(starttime=trim_start, endtime=trim_end)

        # Store new miniseed files in folder titled "Array Miniseed"
        folder = series["folder"]
        if not os.path.isdir(f"{output_dir}{folder}"):
            logger.info(f"Creating folder: {output_dir}{folder}")
            os.mkdir(f"{output_dir}{folder}")

        # Unmask masked array.
        for tr in master:
            if isinstance(tr.data, np.ma.masked_array):
                tr.data = tr.data.filled()
                logger.info(f"{series['folder']} {series['file suffix']}STN{str(series['station number']).zfill(2)} was a masked array.")

        # Write trimmed file to disk.
        fname_out = f"{output_dir}{folder}/{network}.STN{str(series['station number']).zfill(2)}.{series['file suffix']}.{extension}"
        logger.info(f"Extracted {index+1} of {total}. Extracting data from station {str(series['station number']).zfill(2)}. Creating file: {fname_out}.")

        master.write(fname_out, format="mseed")