
"""Convert geographic coordinates between DMS and decimal degrees.

Examples
--------
>>> to_decimal((15, 47, 0, "S"), (35, 0, 0, "E"))
(-15.783333333333333, 35.0)

>>> to_degree(-15.783333333333333, 35.0)
((15, 47, 0.0, 'S'), (35, 0, 0.0, 'E'))
"""

from typing import Tuple, Union

DMSCoordinate = Tuple[int, int, float, str]
DecimalCoordinate = Tuple[float, float]


def to_decimal(
    latitude: DMSCoordinate,
    longitude: DMSCoordinate,
) -> DecimalCoordinate:
    """Convert latitude and longitude from DMS to decimal degrees.

    Parameters
    ----------
    latitude : tuple
        Latitude as (degrees, minutes, seconds, direction).
        Direction must be 'N' or 'S'.
    longitude : tuple
        Longitude as (degrees, minutes, seconds, direction).
        Direction must be 'E' or 'W'.

    Returns
    -------
    tuple of float
        Decimal latitude and decimal longitude. Southern and western
        coordinates are negative.

    Examples
    --------
    >>> to_decimal((15, 47, 0, "S"), (35, 0, 0, "E"))
    (-15.783333333333333, 35.0)
    >>> to_decimal((51, 30, 0, "N"), (0, 7, 0, "W"))
    (51.5, -0.11666666666666667)
    """
    def convert_one(coordinate, valid_directions, max_degrees):
        if len(coordinate) != 4:
            raise ValueError(
                "Each DMS coordinate must contain degrees, "
                "minutes, seconds and direction."
            )

        degrees, minutes, seconds, direction = coordinate
        direction = direction.upper() if isinstance(direction, str) else ""

        if direction not in valid_directions:
            raise ValueError(
                f"Direction must be one of {valid_directions}."
            )

        if not all(
            isinstance(value, (int, float))
            and not isinstance(value, bool)
            for value in (degrees, minutes, seconds)
        ):
            raise TypeError("Degrees, minutes and seconds must be numeric.")

        if degrees < 0 or degrees > max_degrees:
            raise ValueError(
                f"Degrees must be between 0 and {max_degrees}."
            )

        if not 0 <= minutes < 60 or not 0 <= seconds < 60:
            raise ValueError("Minutes and seconds must be in [0, 60).")

        if degrees == max_degrees and (minutes != 0 or seconds != 0):
            raise ValueError(
                f"At {max_degrees} degrees, minutes and seconds must be zero."
            )

        decimal_value = degrees + minutes / 60 + seconds / 3600

        if direction in ("S", "W"):
            decimal_value = -decimal_value

        return decimal_value

    decimal_latitude = convert_one(latitude, ("N", "S"), 90)
    decimal_longitude = convert_one(longitude, ("E", "W"), 180)

    return decimal_latitude, decimal_longitude


def to_degree(
    latitude: float,
    longitude: float,
) -> Tuple[DMSCoordinate, DMSCoordinate]:
    """Convert decimal latitude and longitude to DMS coordinates.

    Parameters
    ----------
    latitude : float
        Decimal latitude between -90 and 90 degrees.
    longitude : float
        Decimal longitude between -180 and 180 degrees.

    Returns
    -------
    tuple
        A pair of DMS tuples in the form
        ((degrees, minutes, seconds, direction),
         (degrees, minutes, seconds, direction)).
        Seconds are returned as floats.

    Examples
    --------
    >>> to_degree(-15.783333333333333, 35.0)
    ((15, 47, 0.0, 'S'), (35, 0, 0.0, 'E'))
    >>> to_degree(51.5, -0.11666666666666667)
    ((51, 30, 0.0, 'N'), (0, 7, 0.0, 'W'))
    """
    def convert_one(value, max_degrees, positive_direction,
                    negative_direction):
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            raise TypeError("Coordinates must be numeric.")

        if not -max_degrees <= value <= max_degrees:
            raise ValueError(
                f"Coordinate must be between {-max_degrees} "
                f"and {max_degrees}."
            )

        direction = negative_direction if value < 0 else positive_direction
        absolute_value = abs(value)

        degrees = int(absolute_value)
        minutes_full = (absolute_value - degrees) * 60
        minutes = int(minutes_full)
        seconds = round((minutes_full - minutes) * 60, 6)

        # Handle rounding that reaches 60 seconds or 60 minutes.
        if seconds >= 60:
            seconds = 0.0
            minutes += 1

        if minutes >= 60:
            minutes = 0
            degrees += 1

        if degrees > max_degrees:
            degrees = max_degrees
            minutes = 0
            seconds = 0.0

        return degrees, minutes, seconds, direction

    dms_latitude = convert_one(latitude, 90, "N", "S")
    dms_longitude = convert_one(longitude, 180, "E", "W")

    return dms_latitude, dms_longitude
