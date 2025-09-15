import sys
import logging

from analytics import numerical_methods


def mean(data: list) -> float:
    """compute the arithmetic mean of a sample dataset.

    Args:
        data (list): list of floats

    Returns:
        float: arithmetic mean of the sample.
    """

    avg = 0
    if isinstance(data, list):
        if not data:
            logging.warning("List size too small")
        else:
            for elem in data:
                if isinstance(elem, (float, int)):
                    avg += elem
                else:
                    logging.warning(
                        f"Datatype does not support numerical ops: {type(elem)}"
                    )
                    avg = 0
            avg = avg / len(data)
    else:
        logging.warning(f"array is not of type list: {type(data)}")

    return avg


def standard_deviation_from_mean(data: list) -> float:
    """compute the standard deviation from the mean of a sample.

    Args:
        data (list): list of floats

    Returns:
        float: standard deviation from the mean.
    """

    sig = 0
    try:
        if len(data) <= 2:
            return 0
        xbar = mean(data)
        N = len(data)
        Nact = 0
        for i in range(N):
            if data[i] != 0.0:
                Nact += 1
                sig += (data[i] - xbar) ** 2
        sig = (sig / (Nact - 1)) ** (0.5)
        sig = sig / (Nact) ** (0.5)
    except ZeroDivisionError:
        logging.debug("Float division by zero, leaving std dev as zero.")
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logging.warning(f"{e} -> Line {exc_tb.tb_lineno}")
    finally:
        return sig


def r_score(x_data: list, y_data: list, coefficients: list) -> tuple[float, float]:
    """compute the coefficient of determination for a curve-fit. (r-score)

    Args:
        x_data (list): _description_
        y_data (list): _description_
        coefficients (list): _description_

    Returns:
        tuple[float, float]: r-score (0-1), variance.
    """
    n = len(x_data)
    sig_y = 0.0
    r2 = 0.0
    SSR = 0
    SST = 0
    y_bar = 0
    try:
        for i in range(n):
            y_bar += y_data[i]
        y_bar = y_bar / n
        y_pred = numerical_methods.polynomial(x_data, coefficients)
        for i in range(n):
            sig_y += (y_data[i] - y_pred[i]) ** 2
            SSR += (y_data[i] - y_pred[i]) ** 2
            SST += (y_data[i] - y_bar) ** 2
        sig_y = sig_y / (n - 2) if n > 2 else sig_y / (n)
        r2 = 1 if SST == 0 else 1 - SSR / SST
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logging.warning(f"{e} -> Line {exc_tb.tb_lineno}")
    finally:
        return r2, (sig_y**(0.5))


def reduced_chi_squared(x_data: list, y_data: list, coefficients: list) -> float:
    """compute teh reduced chi squared test for a model.

    Args:
        x_data (list): _description_
        y_data (list): _description_
        coefficients (list): _description_

    Returns:
        float: reduced chi squared.
    """
    buf = 0
    try:
        y_data_fit = numerical_methods.polynomial(x_data, coefficients)
        buf = sum(
            (y_data[i] - y_data_fit[i]) ** 2 / y_data_fit[i] for i in range(len(y_data))
        )
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logging.warning(f"{e} -> Line {exc_tb.tb_lineno}")
    finally:
        return buf


def moving_average_filter(array: list, value: float, size: int) -> list[float, list]:
    """
    inputs:
        array -> array of floats
        value -> value to append
        size -> size of the array
    outputs:
        avg -> moving average of the array
        array -> current array
    """

    if len(array) > size:
        array.pop(0)

    array.append(value)

    if len(array) < 2:
        average = value
    else:
        average = mean(array)

    return average, array
