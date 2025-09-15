import sys
import math
import logging

from system import settings

from network import get_specs

from analytics import conversion


def compute_full_scale_output(data_max: float, data_min: float) -> float:
    """compute the full scale output of a sensor.

    Args:
        data_max (float): _description_
        data_min (float): _description_

    Returns:
        float: _description_
    """

    return (data_max - data_min) / 2.0


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


def convert_rpm_to_g(rpm: float) -> float:
    """_summary_

    Args:
        rpm (float): _description_

    Returns:
        float: _description_
    """
    return 0


def calculate_resistors_in_parallel(target_resistor):
    logging.info(f"Finding the best combo of resistors that results in {target_resistor}")
    #print(f"target_resistance: {target_resistor}")
    best_diff = 10000000
    r1 = 0
    r2 = 0
    i = 0
    j = 0
    for i in range(len(settings.available_resistors)):
        R1 = float(settings.available_resistors[i])
        #print(f"R1: {R1}")
        i+=1
        if R1 == target_resistor:
            r1 = R1
            r2 = 99999999999999999999999
            best_diff = 0
            best_eq = target_resistor
            break
        elif R1 >= target_resistor:
            for j in range(len(settings.available_resistors)):
                R2 = float(settings.available_resistors[j])
                #print(f"R2: {R2}")
                j +=1
                if R2 >= target_resistor:
                    eq_resistance = 1/((1/R1)+(1/R2))
                    dif_resistance = abs(eq_resistance - target_resistor)
                    if dif_resistance < best_diff:
                        best_diff = dif_resistance
                        best_eq = eq_resistance
                        r1 = R1
                        r2 = R2
                        logging.info(f"The new best resistor combo is: R1 = {r1}, R2 = {r2}")
                        logging.info(f"This combo results in an eq_resistance of: {best_eq}, which is {best_diff} Ohms away from the target of: {target_resistor}")
                        if best_diff == 0:
                            break
    print("The best resistor combo is:")                    
    print("###############################################")
    print(f"R1: {r1}\nR2: {r2}")
    print(f"target resistance: {target_resistor}")
    print(f"eq_resistance: {best_eq}")
    print(f"diff resistance: {best_diff}")
    print("###############################################")
    logging.info(f"The best resistor combo is: R1 = {r1}, R2 = {r2}")
    logging.info(f"This combo results in an eq_resistance of: {best_eq}, which is {best_diff} Ohms away from the target of: {target_resistor}")
    return conversion.convert_resistor_to_string(r1), conversion.convert_resistor_to_string(r2)


