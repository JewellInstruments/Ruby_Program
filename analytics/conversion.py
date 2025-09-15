import math
import logging
from typing import Union


def convert_thermistor_to_temp(R: float, T_0: float, B: float, R_0: float) -> float:
    """convert NTC thermistor to temperature value in C.

    Args:
        R (float): Resistance measured at the thermistor (Ohms)
        T_0 (float): initial temperature as defined by the thermistor definition (K)
        B (float): the B-value as defined by the thermistor definition (1/K)
        R_0 (float): the initial resistance at T_0 as defined by the thermistor (Ohms)
    """
    TEMP_KELVIN = 273.15
    return (T_0 + TEMP_KELVIN) + 1.0 / (B * math.log(R / R_0)) - TEMP_KELVIN  # C


def IFG(latitude: float) -> float:
    """International Gravity Formula 1967 (IFG)

    Args:
        latitude (float): latitude in degrees decimal form

    Returns:
        float: _description_
    """

    latitude = math.radians(latitude)
    return 9.780327 * (
        1.0
        + 0.0053024 * (math.sin(latitude)) ** 2
        - 0.0000058 * (math.sin(2.0 * latitude)) ** 2
    )


def free_air_correction(height: float) -> float:
    """free air correction based on elevation

    Args:
        height (float): height above sea level in meters

    Returns:
        float: free air correction.
    """
    return -3.086 * 1e-6 * height


def local_gravity_correction(latitude: float, height: float) -> float:
    """local gravity based on latitude and elevation

    Args:
        latitude (float): latitude in degrees
        height (float): elevation above sea level in meters

    Returns:
        float: magnitude of gravitational vector field based on elevation and latitude in m/s^2.
    """
    return IFG(latitude) + free_air_correction(height)


def convert_string_to_float(data: str) -> Union[float, None]:
    """take a string and convert to float, if data is unsuccessful, return none.

    Args:
        data (str): string representation of float number

    Returns:
        Union[float, None]: float value of string or None.
    """

    try:
        value = float(data)
    except ValueError:
        return None
    return value


def convert_deg_to_gs(array: list, moa: float = 0.0) -> list:
    """convert a list of deg to g's

    Args:
        array (list): _description_

    Returns:
        list: _description_
    """
    if type(array) is list:
        return [math.sin(math.radians(i - moa)) for i in array]
    else:
        return math.sin(math.radians(array - moa))

def convert_resistor_to_string(resistor):
    ending = "Ohm"
    if resistor > 20000000:
        ending = ""
    elif resistor > 1000000:
        resistor = resistor/1000000
        ending = "M"
    elif resistor > 1000:
        resistor = resistor/1000
        ending = "K"
    if resistor > 20000000:
        res = "DNP"
    else:
        res = str(resistor)
    logging.info(f"Resistor {resistor} converted to {res}")
    return (res + " " + ending)


