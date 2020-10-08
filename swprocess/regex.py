"""Regular expression definitions."""

import re

__all__ = ["get_peak_from_max", "get_all"]


def get_peak_from_max(wavetype="rayleigh", time="(\d+\.?\d*)"):
    """Compile regular expression to extract peaks from a `.max` file.

    Parameters
    ----------
    wavetype : {'rayleigh', 'love', 'vertical', 'radial', 'transverse'}, optional
        Define a specific wavetype to extract, default is `'rayleigh'`.
    time : str, optional
        Define a specific time of interest, default is `"(\d+\.?\d*)")`,
        a generic regular expression which will match all time.

    Return
    ------
    Compiled Regular Expression
        To extract peaks from a `.max` file.

    """
    if wavetype in ["rayleigh", "love", "vertical", "radial", "transverse"]:
        wavetype = wavetype.capitalize()

    number = "-?\d+.?\d*[eE]?[+-]?\d*"
    pattern = f"{time} (\d+\.?\d*) {wavetype} ({number}) ({number}) ({number}) (\d+\.?\d*|-?inf|nan) (\d+\.?\d*) 1"
    return re.compile(pattern)


def get_all(wavetype="rayleigh", time="(\d+\.?\d*)"):
    """Compile regular expression to identify peaks from a `.max` file.

    Parameters
    ----------
    wavetype : {'rayleigh', 'love', 'vertical', 'radial', 'transverse'}, optional
        Define a specific wavetype to extract, default is `'rayleigh'`.
    time : str, optional
        Define a specific time of interest, default is `"(\d+\.?\d*)")`,
        a generic regular expression which will match all time.

    Return
    ------
    Compiled Regular Expression
        To identify peaks from a `.max` file.

    """
    pattern = f"{time} .* {wavetype.capitalize()} .* 1"
    return re.compile(pattern)
