import sys
import math
import logging

from system import stage_configuration
from system import settings

from network import get_specs

from analytics import linear_algebra
from analytics import statistical_methods


def compute_full_scale_output(data_max: float, data_min: float) -> float:
    """compute the full scale output of a sensor.

    Args:
        data_max (float): _description_
        data_min (float): _description_

    Returns:
        float: _description_
    """

    return (data_max - data_min) / 2.0


def compute_pendulous_axis_misalignment(
    data_90_neg: float, data_90_pos: float, scale_factor: float, output_type:str
) -> float:
    """This function computes the pendulous axis misalignment.

    Args:
        data_90_neg (float): output data from sensor while at -90 degrees
        data_90_pos (float): output data from sensor while at 90 degrees

    Returns:
        float: pendulous axis misalignment in degrees.
    """
    try:
        if output_type == "0-5 vdc":
            offset = 2.5
        elif output_type == "+/-5 vdc":
            offset = 0
        elif output_type == "4-20ma":
            offset = 12
        else:
            #TODO: print("digital unit")
            offset = 0
        #print(f"data_90_neg: {data_90_neg}")
        #print(f"data_90_pos: {data_90_pos}")
        data_90_neg = data_90_neg - offset
        data_90_pos = data_90_pos - offset
        Mpa = math.degrees(
            math.asin(
                (data_90_pos - data_90_neg)
                / (2.0 * stage_configuration.LOCAL_G_VALUE * scale_factor)
            )
        )
        logging.info(f"{data_90_pos+offset} {data_90_neg+offset} {Mpa}")
        return Mpa

    except Exception as e:
        print(f"{settings.red_text}scale factor is {scale_factor}{settings.white_text}")
        print(f"pos: {data_90_pos}")
        print(f"neg: {data_90_neg}")
        print(f"g: {stage_configuration.LOCAL_G_VALUE}")
        print(e)
        try:
            return math.degrees(
                math.asin(
                    (data_90_pos - data_90_neg)
                    / (2.0 * stage_configuration.LOCAL_G_VALUE * int(scale_factor))
                )
            )
        except Exception as ex:
            print(
                (data_90_pos - data_90_neg)
                / (2.0 * stage_configuration.LOCAL_G_VALUE * scale_factor)
            )
            print(ex)
            return 9999999


def compute_output_axis(data_0: float, data_180: float, scale_factor: float) -> float: #does this work for ma units?
    """This function computes the output axis misalignment

    Args:
        data_0 (float): output data from sensor while at 0 degrees
        data_180 (float): output data from sensor while at 180 degrees.
        scale_factor (float): the scale factor of the UUT in V/g.

    Returns:
        float: output axis misalignment in volts
    """
    try:
        Moa = math.degrees(
            math.asin(
                (data_0 - data_180)
                / (2.0 * stage_configuration.LOCAL_G_VALUE * scale_factor)
            )
        )
        logging.info(f"{data_0} {data_180} {Moa}")
        return Moa
    except Exception as e:
        print(
            f"{settings.red_text}scale factor is probably 0 or something else when wrong with the math{settings.white_text}"
        )
        print(e)

        return 90


def compute_input_axis_misalignment(Moa: float, Mpa: float) -> float:
    """calculate the input axis misalignment of servo-forced balanced sensor.

    Args:
        Moa (float): Output axis misalignment in degrees
        Mpa (float): Pendulous axis misalignment in degrees

    Returns:
        float: input axis misalignment in degrees
    """

    return math.sqrt(Mpa**2 + Moa**2)


def compute_bias(data_0: float, data_180: float, scale_factor: float, output_type:str, axis:int = 0) -> float:
    """This function computes the bias

    Args:
        data_0 (float): output data from sensor while at 0 <V, mA>.
        data_180 (float): output data from sensor while at 180 <V, mA>.
        scale_factor (float): the scale factor of the UUT in <V, mA>/g.

    Returns:
        float: bias in g's.
    """
    if output_type == "4-20ma":
        offset = 0#12.0
        #offset_tolerance = 2.0
    elif output_type == "0-5 vdc":
        offset = 2.5
    elif output_type == "+/-5 vdc":
        offset = 0
    else:
        #TODO:digital unit
        offset = 0
    #if axis == 2:
    #        offset = offset + (scale_factor)
    #if (abs(data_0 - mA_offset) < mA_offset_tolerance and abs(data_180 - mA_offset) < mA_offset_tolerance):  # allowed 10 to 14 mA
    data_0 = data_0 - offset
    data_180 = data_180 - offset

    bias = (data_0 + data_180) / (2.0 * scale_factor)
    logging.info(f"{data_0} {data_180} {bias}")
    return bias


def polynomial(data: list, coefficients: list) -> list:
    """build polynomial using coefficients which provide the c0,c1,c2..cn in a list respectively.

    Args:
        data (list): data to be used for the basis of the polynomial function
        coefficients (list): list of coefficients for the polynomial. y = c0 + cn*x**n for n in len(coefficients)

    Returns:
        list: output data from the polynomial using data as the basis and coefficients as the coefficients.
    """
    return [
        sum(coefficients[m] * data[i] ** m for m in range(len(coefficients)))
        for i in range(len(data))
    ]


def nonlinearity(x_data: list, y_data: list, coefficients: list) -> float:
    """calculate the maximum deviation from a best fit straight line.

    Args:
        x_data (list): x data to be used in the curve fitting process.
        y_data (list): y data to be used in the curve fitting process.
        coefficients (list): coefficients to be used for the polynomial.

    Returns:
        float: maximum deviation from the best fit straight line as a percent of the full range.
    """
    error_method = "std"
    max_err = 0
    try:
        y_data_fit = polynomial(x_data, coefficients)
        err = []
        for i in range(len(x_data)):
            buf = abs(y_data_fit[i] - y_data[i])
            err.append(100 * buf / (max(y_data) - min(y_data)))
        max_err = max(err)
        # std_err = (statistics.stdev(err)) / (math.sqrt(len(err)))
        std_err = standard_error(err)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logging.warning(f"{e} -> Line {exc_tb.tb_lineno}")
    finally:
        if error_method == "max":
            return max_err
        elif error_method == "std":
            return std_err
        else:
            return std_err


def validate_angle(angle: float) -> int:
    """validate the angle is not none"""
    return 1 if angle is not None else 0


def calculate_bias_over_temp(
    data: list, specs: get_specs.mems_specs, axis_index: int
) -> tuple[float, float]:
    """_summary_

    Args:
        data (list): _description_
        specs (get_specs.mems_specs): _description_
        axis_index (int): _description_

    Returns:
        tuple[float, float]: _description_
    """
    bts = 0.0
    average_plate_temp = []
    bias = []
    # loop over all the data for that axis.
    for arr in data:
        # initialize some lists for data
        plate_temp = []
        output = []
        angle = []

        zero_tilt = []

        # select the zero tilt based on which axis one is looking at.
        if axis_index == 0:
            zero_tilt.append(arr[len(arr) // 2][9])
        elif axis_index == 1:
            zero_tilt.append(arr[len(arr) // 2][10])
        elif axis_index == 2:
            zero_tilt.append(arr[len(arr) // 2][11])
        else:
            zero_tilt.append(arr[len(arr) // 2][12])

        # bulb up the data arrays by looping over each record.
        for record in arr:
            # print(record)
            plate_temp.append(record[8])
            angle.append(record[7])
            # select the correct output based on axis of interest.
            if axis_index == 0:
                output.append(record[9])
                bts_limit = specs.bts0
                bias_limit = specs.bias0
            elif axis_index == 1:
                output.append(record[10])
                bts_limit = specs.bts1
                bias_limit = specs.bias0
            elif axis_index == 2:
                output.append(record[11])
                bts_limit = specs.bts2
                bias_limit = specs.bias0
            else:
                output.append(record[9])

        # use the first order regression to get the bias (y intercept)
        soln, *_ = linear_algebra.solve_least_sqrs(angle, output, order=1)
        # print(soln)

        bias.append(soln[0])
        average_plate_temp.append(statistical_methods.mean(plate_temp))

    # perform a cubic regression using the plate temp and the bias.
    coefficients, *_ = linear_algebra.solve_least_squares(
        average_plate_temp, bias, order=3
    )

    # use the cubic regreesion model to solve for the bias at 25 C.
    bias_25C = polynomial([25], coefficients)

    bias_25C = bias_25C[0]

    # bias temperature sensitivity in units of ppm/C
    bts = 1e6 * (
        abs(
            (zero_tilt[0] - zero_tilt[-1])
            / (average_plate_temp[0] - average_plate_temp[-1])
        )
    )

    # display the results

    if abs(bias_25C) > bias_limit:
        print(
            "Bias at 25 C for the {} axis: \033[91m{:.4f}\033[00m (deg)".format(
                stage_configuration.AXES_DECODER[str(axis_index)], bias_25C
            )
        )
    else:
        print(
            "Bias at 25 C for the {} axis: \033[92m{:.4f}\033[00m (deg)".format(
                stage_configuration.AXES_DECODER[str(axis_index)], bias_25C
            )
        )

    if abs(bts) > bts_limit:
        print(
            "BTS for the {} axis: \033[91m{:.4f}\033[00m (ppm/C)".format(
                stage_configuration.AXES_DECODER[str(axis_index)], bts
            )
        )
    else:
        print(
            "BTS for the {} axis: \033[92m{:.4f}\033[00m (ppm/C)".format(
                stage_configuration.AXES_DECODER[str(axis_index)], bts
            )
        )

    return bias_25C, bts


def calculate_accuracy(
    data: list, specs: get_specs.mems_specs, axis_index: int
) -> float:
    """_summary_

    Args:
        data (list): _description_
        specs (get_specs.mems_specs): _description_
        axis_index (int): _description_

    Returns:
        float: _description_
    """
    bias_25C, bts = calculate_bias_over_temp(data, specs, axis_index)

    accuracy = []

    for arr in data:
        # initialize some lists for data
        output = 0.0
        angle = 0.0

        # buld up the data arrays by looping over each record.
        for record in arr:
            # print(record)
            angle = record[7]
            # select the correct output based on axis of interest.
            if axis_index == 0:
                output = record[9]
                accry_limit = specs.accy0
            elif axis_index == 1:
                output = record[10]
                accry_limit = specs.accy1
            elif axis_index == 2:
                output = record[11]
                accry_limit = specs.accy2
            else:
                output = record[9]

            accuracy.append(abs(angle - (output + bias_25C)))

    relative_accuracy = max(accuracy)

    if abs(relative_accuracy) > accry_limit:
        print(
            "Relative accuracy for the {} axis: \033[91m{:.4f}\033[00m (deg)".format(
                stage_configuration.AXES_DECODER[str(axis_index)], relative_accuracy
            )
        )
    else:
        print(
            "Relative accuracy for the {} axis: \033[92m{:.4f}\033[00m (deg)".format(
                stage_configuration.AXES_DECODER[str(axis_index)], relative_accuracy
            )
        )

    return relative_accuracy


def calculate_linearity(
    data: list, specs: get_specs.mems_specs, axis_index: int
) -> float:
    """_summary_

    Args:
        data (list):  A, X, Y, Z, UT, PT,
        specs (get_specs.mems_specs): _description_
        axis_index (int): _description_

    Returns:
        float: _description_
    """
    calculated_angle = 0.0
    max_nonlinearity = 0.0
    nonlinearity = []

    linearity_limit = specs.linearity[axis_index]

    for arr in data:
        # initialize some lists for data
        output = []
        angle = []

        # build up the data arrays by looping over each record.
        for record in arr:
            # print(record)
            angle.append(record[0])
            # select the correct output based on axis of interest.
            if axis_index == 0:
                output.append(record[1])
            elif axis_index == 1:
                output.append(record[2])
            elif axis_index == 2:
                output.append(record[3])
            else:
                output.append(record[1])

        # print(angle)
        # print(output)
        coefficients, *_ = linear_algebra.solve_least_squares(output, angle, order=1)

        calculated_angle = polynomial(output, coefficients)

        nonlinearity.extend(
            100.0 * abs(calculated_angle[i] - angle[i]) / (max(angle) - min(angle))
            for i in range(len(angle))
        )
    max_nonlinearity = max(nonlinearity)

    if max_nonlinearity > linearity_limit:
        print(
            "linearity for the {} axis: \033[91m{:.4f}\033[00m (% FS)".format(
                stage_configuration.AXES_DECODER[str(axis_index)], max_nonlinearity
            )
        )
    else:
        print(
            "linearity for the {} axis: \033[92m{:.4f}\033[00m (% FS)".format(
                stage_configuration.AXES_DECODER[str(axis_index)], max_nonlinearity
            )
        )

    return max_nonlinearity


def calculate_verification_accuracy(
    data: list, specs: get_specs.mems_specs, axis_index: int
) -> None:
    """_summary_

    Args:
        data (list): [A, X, Y, Z, UT, PT]
        specs (get_specs.mems_specs): _description_
        axis_index (int): _description_
    """
    error = []
    for arr in data:
        # build up the data arrays by looping over each record.
        for record in arr:
            # print(record)
            angle = record[0]
            # select the correct output based on axis of interest.
            if axis_index == 0:
                output = record[1]
            elif axis_index == 1:
                output = record[2]
            elif axis_index == 2:
                output = record[3]
            error.append(angle - output)

    if abs(max(error)) > specs.accuracy[axis_index]:
        print(
            f"Max Error ({specs.output_units}) for {axis_index} Axis: \033[91m{max(error):.5f}\033[00m"
        )
    else:
        print(
            f"Max Error ({specs.output_units}) for {axis_index} Axis: \033[92m{max(error):.5f}\033[00m"
        )


def calculate_cross_axis_error(
    data: list, specs: get_specs.mems_specs, axis_index: int
) -> None:
    """_summary_

    Args:
        data (list): _description_
        specs (get_specs.mems_specs): _description_
        axis_index (int): _description_
    """
    error = []
    for arr in data:
        # build up the data arrays by looping over each record.
        for record in arr:
            if axis_index == 0:
                output = record[2]
            elif axis_index == 1:
                output = record[1]
            elif axis_index == 2:
                output = record[1]
            error.append(output)

    if abs(max(error)) > specs.mpa[axis_index]:
        print(
            f"Max Cross Axis Error ({specs.output_units}) for {axis_index} Axis: \033[91m{max(error):.5f}\033[00m"
        )
    else:
        print(
            f"Max Cross Axis Error ({specs.output_units}) for {axis_index} Axis: \033[92m{max(error):.5f}\033[00m"
        )


def standard_error(data: list) -> float:
    """Some BS "math" our esteemed "really smart" engineers came up with to make sensors pass linearity because they couldn't figure out how to properly communicate with instrumentation or analyze datasets.

    Args:
        data (list): _description_

    Returns:
        float: _description_
    """
    std_error_value = 0
    try:
        sum_of_sqrs = sum([i**2 for i in data])
        sq_of_sums = sum(data) ** 2

        # logging.info(sum_of_sqrs)
        # logging.info(sq_of_sums)
        # logging.info(len(data))

        std_error_value = math.sqrt(
            1.0 / (len(data) - 2) * abs((sum_of_sqrs - 1.0 / len(data) * sq_of_sums))
        )
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        error = f"Error occurred at {exc_tb.tb_lineno} - {e}"
        print(error)
        logging.warning(error)
    return std_error_value


def compute_bias_temperature_sensitivity(
    bias_array: list, temperature_array: list, method: str = "Standard"
) -> list[list, list]:
    """see Force_Balance_Temp_Comp_Review.pdf

    Args:
        bias_array (list): _description_
        temperature_array (list): _description_

    Returns:
        list: a list of bts and a list of temps that correspond to that bts for that temp keyed by index in both arrays.
    """
    try:

        bts_array = []
        temp_array = []

        if method == "Standard":

            room_temp_index = 0
            for index in range(len(temperature_array)):
                if abs(temperature_array[index] - 22.5) < 5:
                    room_temp_index = index

            for index in range(len(temperature_array)):
                if index == room_temp_index:
                    pass
                else:
                    delta_temp = (
                        temperature_array[index] - temperature_array[room_temp_index]
                    )
                    delta_bias = bias_array[index] - bias_array[room_temp_index]
                    bts = delta_bias / delta_temp

                    logging.info(f"{bts}, {temperature_array[index]}")

                    bts_array.append(bts)
                    temp_array.append(temperature_array[index])
        else:
            print("whoa boi, this is not good. ")

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        error = f"Error occurred at {exc_tb.tb_lineno} - {e}"
        print(error)
        logging.warning(error)

    return bts_array, temp_array


def compute_scale_factor_temperature_sensitivity(
    scale_factors_array: list, temperature_array: list, method: str = "Standard"
) -> list:
    """see Force_Balance_Temp_Comp_Review.pdf

    Args:
        scale_factors_array (list): _description_
        temperature_array (list): _description_

    Returns:
        list: _description_
    """
    try:

        sfts_array = []
        temp_array = []

        if method == "Standard":

            room_temp_index = 0
            for index in range(len(temperature_array)):
                if abs(temperature_array[index] - 22.5) < 5:
                    room_temp_index = index

            for index in range(len(temperature_array)):
                if index == room_temp_index:
                    pass
                else:
                    delta_temp = (
                        temperature_array[index] - temperature_array[room_temp_index]
                    )
                    delta_scale_factor = (
                        scale_factors_array[index]
                        / scale_factors_array[room_temp_index]
                        - 1.0
                    )
                    sfts = delta_scale_factor / delta_temp * 1e6  # ppm/c
                    logging.info(f"{sfts}, {temperature_array[index]}")

                    sfts_array.append(sfts)
                    temp_array.append(temperature_array[index])
        else:
            print("whoa boi, this is not good. ")

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        error = f"Error occurred at {exc_tb.tb_lineno} - {e}"
        print(error)
        logging.warning(error)

    return sfts_array, temp_array


def calculate_rpm(acceleration: float, radius: float) -> float:
    """See derivation in Standard_Equations_for_Calibration_of_Servo_Accelerometer.pdf on http://webserver01. This method
    calculates the rpm required to attain a g force given a known radius from rotation.

    Args:
        acceleration (float): in g's
        radius (float): in meters

    Returns:
        float: output in rpm
    """
    g = stage_configuration.LOCAL_G_VALUE  # m/s^2

    rpm = math.sqrt((3600.0 * g * acceleration) / (4.0 * math.pi**2 * radius))

    return rpm


def convert_rpm_to_g(rpm: float) -> float:
    """_summary_

    Args:
        rpm (float): _description_

    Returns:
        float: _description_
    """
    return 0
