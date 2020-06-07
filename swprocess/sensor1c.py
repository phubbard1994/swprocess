"""Sensor1C class definition."""

import logging

from swprocess import ActiveTimeSeries

logger = logging.getLogger(name=__name__)


class Sensor1C(ActiveTimeSeries):
    """Class for single component sensor objects."""

    def _set_position(self, x, y, z):
        self._x = float(x)
        self._y = float(y)
        self._z = float(z)

    def __init__(self, amplitude, dt, x, y, z, nstacks=1, delay=0):
        """Initialize `Sensor1C`."""
        super().__init__(amplitude, dt, nstacks=nstacks, delay=delay)
        self._set_position(x, y, z)

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    @property
    def z(self):
        return self._z

    @classmethod
    def from_sensor1c(cls, sensor1c):
        attrs = ["amplitude", "dt", "x", "y", "z"]
        args = [getattr(sensor1c, attr) for attr in attrs]
        kwargs = {key: getattr(sensor1c, key) for key in ["nstacks", "delay"]}
        return cls(*args, **kwargs)

    @classmethod
    def from_activetimeseries(cls, activetimeseries, x, y, z):
        return cls(activetimeseries.amp, activetimeseries.dt, x, y, z,
                   nstacks=activetimeseries.nstacks,
                   delay=activetimeseries.delay)

    @classmethod
    def from_trace(cls, trace, read_header=True,
                   nstacks=1, delay=0, x=0, y=0, z=0):
        """Create a `Sensor1C` object from a `Trace` object.

        Parameters
        ----------
        trace : Trace
            `Trace` object with attributes `data` and `stats.delta`.
        read_header : bool
            Flag to indicate whether the data in the header of the
            file should be parsed, default is `True` indicating that
            the header data will be read.
        nstacks : int, optional
            Number of stacks included in the present trace, default
            is 1 (i.e., no stacking). Ignored if `read_header=True`.
        delay : float, optional
            Pre-trigger delay in seconds, default is 0 seconds.
            Ignored if `read_header=True`.
        x, y, z : float, optional
            Receiver's relative position in x, y, and z, default is
            zero for all components (i.e., the origin). Ignored if
            `read_header=True`.

        Returns
        -------
        Sensor1C
            An initialized `Sensor1C` object.

        Raises
        ------
        ValueError
            If trace type cannot be identified.

        """
        try:
            _format = trace.stats._format.upper()
        except:
            raise ValueError("Trace type could not be identified.")

        if read_header:
            if _format == "SEG2":
                return cls._from_trace_seg2(trace)
            elif _format == "SU":
                return cls._from_trace_su(trace)
            else:
                raise NotImplementedError
        else:
            return cls(amplitude=trace.data, dt=trace.stats.delta,
                       x=x, y=y, z=z,  nstacks=nstacks, delay=delay)

    @classmethod
    def _from_trace_seg2(cls, trace):
        """Create a `Sensor1C` object form a SEG2-style `Trace` object.

        Parameters
        ----------
        trace : Trace
            SEG2-style Trace with header information entered correctly.

        Returns
        -------
        Sensor1C
            An initialized `Sensor1C` object.

        """
        header = trace.stats.seg2
        return cls.from_trace(trace,
                              read_header=False,
                              nstacks=int(header.STACK),
                              delay=float(header.DELAY),
                              x=float(header.RECEIVER_LOCATION),
                              y=0,
                              z=0)

    @classmethod
    def _from_trace_su(cls, trace):
        """Create a `Sensor1C` object form a SU-style `Trace` object.

        Parameters
        ----------
        trace : Trace
            SU-style trace with header information entered correctly.

        Returns
        -------
        Sensor1C
            An initialized `Sensor1C` object.

        """
        header = trace.stats.su.trace_header
        nstack_key = "number_of_horizontally_stacked_traces_yielding_this_trace"
        return cls.from_trace(trace,
                              read_header=False,
                              nstacks=int(header[nstack_key])+1,
                              delay=float(header["delay_recording_time"]),
                              x=float(header["group_coordinate_x"]/1000),
                              y=float(header["group_coordinate_y"]/1000),
                              z=0)

    def _is_similar(self, other, exclude=[]):
        """Check if `other` is similar to `self` though not equal."""
        if not isinstance(other, Sensor1C):
            return False

        for attr in ["x", "y", "z"]:
            if attr in exclude:
                continue
            if getattr(self, attr) != getattr(other, attr):
                return False

        if not super()._is_similar(other, exclude=exclude):
            return False

        return True

    def __eq__(self, other):
        """Check if `other` is equal to the `Sensor1C`."""
        if not super().__eq__(other):
            return False

        return True