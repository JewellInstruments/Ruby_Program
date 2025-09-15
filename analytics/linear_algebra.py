import itertools
import logging
import sys

from analytics import statistical_methods

from network import get_specs


def zeros_matrix(rows: int, cols: int) -> list:
    """build a matrix with zeros.

    Args:
        rows (int): _description_
        cols (int): _description_

    Returns:
        list: a matrix with zeros.
    """
    A = []
    for _ in range(rows):
        A.append([])
        for _ in range(cols):
            A[-1].append(0.0)

    return A


def get_shape(matrix: list) -> tuple[int, int]:
    """get the shape of a matrix.

    Args:
        matrix (list): _description_

    Returns:
        tuple[int, int]: rows, columns
    """
    rows = len(matrix)
    cols = len(matrix[0])

    return rows, cols


def add_matrix(matrix_1: list, matrix_2: list) -> list:
    rows_a, cols_a = get_shape(matrix_1)
    rows_b, cols_b = get_shape(matrix_2)
    if (rows_a != rows_b) or (cols_a != cols_b):
        return None

    C = zeros_matrix(rows_a, cols_a)

    for i, j in itertools.product(range(rows_a), range(cols_a)):
        C[i][j] = matrix_1[i][j] + matrix_2[i][j]

    return C


def subtract_matrix(matrix_1: list, matrix_2: list) -> list:
    """subtract two matrices

    Args:
        matrix_1 (list): _description_
        matrix_2 (list): _description_

    Returns:
        list: _description_
    """
    rows_a, cols_a = get_shape(matrix_1)
    rows_b, cols_b = get_shape(matrix_2)
    if (rows_a != rows_b) or (cols_a != cols_b):
        return None

    C = zeros_matrix(rows_a, cols_a)

    for i, j in itertools.product(range(rows_a), range(cols_a)):
        C[i][j] = matrix_1[i][j] - matrix_2[i][j]

    return C


def matrix_multiply(matrix_1: list, matrix_2: list) -> list:
    """multiply two matrices together.

    Args:
        matrix_1 (list): _description_
        matrix_2 (list): _description_

    Returns:
        list: _description_
    """
    rowsA = len(matrix_1)
    colsA = len(matrix_1[0])

    rowsB = len(matrix_2)
    colsB = len(matrix_2[0])

    if colsA != rowsB:
        print("Number of A columns must equal number of B rows.")
        sys.exit()

    C = zeros_matrix(rowsA, colsB)

    for i, j in itertools.product(range(rowsA), range(colsB)):
        total = sum(matrix_1[i][ii] * matrix_2[ii][j] for ii in range(colsA))
        C[i][j] = total

    return C


def scale_matrix(matrix: list, scale: float) -> list:
    """scale a matrix.

    Args:
        matrix (list): _description_
        scale (float): _description_

    Returns:
        list: scaled matrix.
    """
    rows, cols = get_shape(matrix)
    for i, j in itertools.product(range(rows), range(cols)):
        matrix[i][j] = matrix[i][j] * scale

    return matrix


def check_matrix_equality(
    matrix_1: list, matrix_2: list, tolerance: float = 0.0
) -> bool:
    """check if two matrices are equal to within some tolerance.

    Args:
        matrix_1 (list): _description_
        matrix_2 (list): _description_
        tol (float, optional): _description_. Defaults to 0.0.

    Returns:
        bool: _description_
    """
    return 1


def identity_matrix(n: int) -> list:
    """build the identity matrix of shape n x n.

    Args:
        n (int): shape of the matrix

    Returns:
        list: identity matrix of shape n x n.
    """
    identity = zeros_matrix(n, n)

    for i, j in itertools.product(range(n), range(n)):
        if i == j:
            identity[i][j] = 1.0
    return identity


def check_squareness(matrix: list) -> bool:
    """_summary_

    Args:
        matrix (list): _description_

    Returns:
        bool: _description_
    """
    return True if len(matrix) == len(matrix[0]) else False


def invert_matrix(matrix: list, tol=None):
    """
    Returns the inverse of the passed in matrix.
        :param A: The matrix to be inverse

        :return: The inverse of the matrix A
    """
    # Section 1: Make sure A can be inverted.
    check_squareness(matrix)
    # check_non_singular(A)

    # Section 2: Make copies of A & I, AM & IM, to use for row ops
    n = len(matrix)
    identity = identity_matrix(n)

    # Section 3: Perform row operations
    indices = list(range(n))  # to allow flexible row referencing ***
    for fd in range(n):  # fd stands for focus diagonal
        fdScaler = 1.0 / matrix[fd][fd]
        # FIRST: scale fd row with fd inverse.
        for j in range(n):  # Use j to indicate column looping.
            matrix[fd][j] *= fdScaler
            identity[fd][j] *= fdScaler
        # SECOND: operate on all rows except fd row as follows:
        for i in indices[:fd] + indices[fd + 1 :]:
            # *** skip row with fd in it.
            crScaler = matrix[i][fd]  # cr stands for "current row".
            for j in range(n):
                # cr - crScaler * fdRow, but one element at a time.
                matrix[i][j] = matrix[i][j] - crScaler * matrix[fd][j]
                identity[i][j] = identity[i][j] - crScaler * identity[fd][j]

    # Section 4: Make sure IM is an inverse of A with specified tolerance

    if check_matrix_equality(identity, matrix_multiply(matrix, identity), tol):
        return identity
    else:
        raise ArithmeticError("Matrix inverse out of tolerance.")


def build_A_matrix(x_data: list, order: int) -> list:
    """_summary_

    Args:
        x_data (list): dataset
        order (int): degree of polynomial used for curve-fitting

    Returns:
        list: an order x order list of lists representing a matrix
    """
    A = [[0 for _ in range(order)] for _ in range(order)]
    for i, j in itertools.product(range(order), range(order)):
        A[i][j] = sum(k ** (i + j) for k in x_data)
    return A


def build_B_matrix(x_data: list, y_data: list, order: int) -> list:
    """build the B matrix in the linear regression model.

    Args:
        x_data (list): _description_
        y_data (list): _description_
        order (int): degree of polynomial used for curve-fitting

    Returns:
        list: an order x order list of lists representing a matrix
    """
    B = [[0] for _ in range(order)]
    for i in range(order):
        B[i][0] = sum(x_data[j] ** i * y_data[j] for j in range(len(x_data)))
    return B


def solve_least_squares(
    x_data: list, y_data: list, order: int
) -> tuple[float, float, float]:
    """solve linear regression equations for n-th order polynomial where n = order. The general matrix equation is Ax = B where
    A is an n x n matrix, x is the coefficient n x 1 matrix that we are solving for and B is the n x 1 matrix. See Mathematical Proof of Nth Order Linear
    Regression Model on http://192.168.3.11/documents for derivation. The solution to the matrix equation requires x = A^-1 B where A^{-1}A = I. A^-1 is calculated
    using the gaussian elimination method for n x n matrices.

    Args:
        x_data (list): x dataset for curve-fitting
        y_data (list): y dataset for curve-fitting
        order (int): degree of polynomial to use

    Returns:
        tuple[float, float, float]: coefficients, fit-error, r-score value
    """
    coefficients = [0 for _ in range(order + 1)]
    r2 = 0
    sig_y = 0
    try:
        m = order + 1
        AM = build_A_matrix(x_data, m)
        # print(f"x data: {x_data}")
        # print(f"y data: {y_data}")
        # print(f"m: {m}")

        BM = build_B_matrix(x_data, y_data, m)
        n = len(AM)
        # GAUSSIAN ELIMINATION METHOD WITH PIVOTING
        indices = list(range(n))  # allow flexible row referencing ***
        for fd in range(n):  # fd stands for focus diagonal
            fdScaler = 0.0 if AM[fd][fd] == 0 else 1.0 / AM[fd][fd]
            # FIRST: scale fd row with fd inverse.
            for j in range(n):  # Use j to indicate column looping.
                AM[fd][j] *= fdScaler
            BM[fd][0] *= fdScaler

            # SECOND: operate on all rows except fd row.
            for i in indices[:fd] + indices[fd + 1 :]:  # *** skip fd row.
                crScaler = AM[i][fd]  # cr stands for "current row".
                for j in range(n):  # cr - crScaler*fdRow.
                    AM[i][j] = AM[i][j] - crScaler * AM[fd][j]
                BM[i][0] = BM[i][0] - crScaler * BM[fd][0]

        for elem in range(len(BM)):
            coefficients[elem] = BM[elem][0]

        r2, sig_y = statistical_methods.r_score(
            x_data, y_data, coefficients
        )  # this is the issue

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logging.warning(f"{e} -> Line {exc_tb.tb_lineno}")

    finally:
        return coefficients, sig_y, r2


def display_matrix_orthonormal_matrix(
    matrix: list, specs: get_specs.mems_specs
) -> None:
    """display a matrix of n x m on terminal for easy viewing.

    Args:
        matrix (list): matrix to print.
        specs (get_specs.mems_specs): product definition for color coding results.
    """
    str_to_print = ""
    for i in range(len(matrix)):
        str_to_print += "| "
        for j in range(len(matrix[i])):
            if i == j:
                if abs(matrix[i][j] - 1) < specs.orthonormal_element_limit:
                    color = "\033[92m"  # green
                else:
                    color = "\033[91m"  # red
            else:
                if abs(matrix[i][j]) < specs.orthonormal_element_limit:
                    color = "\033[92m"  # green
                else:
                    color = "\033[91m"  # red
            str_to_print += f"{color}{matrix[i][j]:.4f}\033[00m "

        str_to_print += "|\n"
    print(str_to_print)
    return


def display_matrix_offset_matrix(matrix: list, specs: get_specs.mems_specs) -> None:
    """display a matrix of n x 1 on terminal for easy viewing.

    Args:
        matrix (list): matrix to print.
        specs (get_specs.mems_specs): product definition for color coding results.
    """
    str_to_print = ""
    color = "\033[92m"  # green
    for i in range(len(matrix)):
        str_to_print += "| "
        if abs(matrix[i]) > specs.offset_matrix_limits[i]:
            color = "\033[91m"  # red
        str_to_print += f"{color}{matrix[i]:.2f}\033[00m"
        str_to_print += "|\n"
    print(str_to_print)
    return


def average_columns(matrix: list) -> list:
    """_summary_

    Args:
        matrix (list): _description_

    Returns:
        list: _description_
    """

    average_matrix = []
    for column in range(len(matrix[0])):
        average = 0.0
        for row in range(len(matrix)):
            average += matrix[row][column]
        average_matrix.append(average / len(matrix))
    return average_matrix


def average_rows(matrix: list) -> list:
    """_summary_

    Args:
        matrix (list): _description_

    Returns:
        list: _description_
    """

    average_matrix = []
    for row in range(len(matrix)):
        average = 0.0
        for column in range(len(matrix[0])):
            average += matrix[row][column]
        average_matrix.append(average / len(matrix))
    return average_matrix
