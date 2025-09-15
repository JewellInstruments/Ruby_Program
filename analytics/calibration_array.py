import math


def build_calibration_array(input_range: float, points: int, input_type: str) -> list:
    """build the array of points in degrees used for calibration if not specified.

    Args:
        input_range (float): range of the sensor either in g's or degrees.
        points (int): number of calibration points (must be odd and greater than 3)
        input_type (str): either accelerometer or inclinometer,

    Returns:
        list: list of points to move the stage to in degrees
    """
    if input_range > 1 and input_type.upper() not in ["ACCELEROMETER", "INCLINOMETER"]:
        print(
            f"something is wrong with the unit's type of sensor: {input_type}. should be inclinometer or accelerometer"
        )

    elif input_type.upper() == "ACCELEROMETER":
        return [
            math.degrees(math.asin(-input_range + 2 * input_range * i / (points - 1)))
            for i in range(points)
        ]
    else:
        return [
            -input_range + 2 * input_range * i / (points - 1) for i in range(points)
        ]
