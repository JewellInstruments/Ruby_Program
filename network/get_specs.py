from network import api_calls

from analytics import calibration_array

from system import settings


class mems_specs:
    def __init__(self, part_no: str):

        data_basic = api_calls.get_part_number_definition(part_no)
        # print(data_basic)

        self.part_no = data_basic["part_no"]
        self.model_no = data_basic["model_no"]
        self.sensor_type = data_basic["specs"]["sensor_type"].lower()
        self.output_type = data_basic["specs"]["output_type"].lower()
        if (self.output_type == "+/-5 vdc") or (self.output_type == "0-5 vdc"):
            self.output_method = "analog_voltage"
        elif self.output_type == "4-20ma":
            self.output_method = "analog_current"
        elif self.output_type == "digital":
            self.output_method = "digital"
        else:
            print(
                f"{settings.red_text}Warning: output type is unexpected: {self.output_type}{settings.white_text}"
            )
            self.output_method = "analog_voltage"

        self.input_units = data_basic["specs"]["input_units"]
        self.output_units = data_basic["specs"]["output_units"]
        self.thermal_destress = data_basic["specs"]["thermal_destress"]
        self.cycles = data_basic["specs"]["cycles"]
        self.soak_time = data_basic["specs"]["soak_time"]
        self.linearity_points = data_basic["specs"]["linearity_points"]
        self.extra_points = data_basic["specs"]["extra_points"]
        self.settle_time = data_basic["specs"]["settle_time"]
        self.num_temps = data_basic["specs"]["num_temps"]
        self.cal_temps = data_basic["specs"]["cal_temps"]
        self.cal_temp_tol = data_basic["specs"]["cal_temp_tol"]
        self.verify_temps = data_basic["specs"]["verify_temps"]
        self.verify_temp_tol = data_basic["specs"]["verify_temp_tol"]
        self.start_stop_step_temps = data_basic["specs"]["start_stop_step_temps"]
        self.test_voltage = data_basic["specs"]["test_voltage"]
        self.input_current = data_basic["specs"]["input_current"]
        self.high_line = data_basic["specs"]["high_line"]  # default 18
        self.low_line = data_basic["specs"]["low_line"]  # default 12
        self.dual_supply = data_basic["specs"]["dual_supply"]  # default false
        self.scale_factor_tolerance = data_basic["specs"][
            "scale_factor_tolerance"
        ]  # default 0
        self.is_digital = data_basic["is_digital"]

        self.digital_type = ""

        if self.is_digital is True:
            self.digital_type = data_basic["digital"]["digital_type"]
            self.baud = data_basic["digital"]["baud"]
            self.data_bits = data_basic["digital"]["data_bits"]
            self.stop_bits = data_basic["digital"]["stop_bits"]
            self.parity = data_basic["digital"]["parity"]
            self.sample_rate = data_basic["digital"]["sample_rate"]
            self.filtering = data_basic["digital"]["filtering"]
            self.modbus = False

        self.linearity = [data_basic["specs"]["linearity"][0] for _ in range(3)]
        self.axes_no = data_basic["specs"]["axes_no"]
        self.range = [data_basic["specs"]["range"][0] for _ in range(3)]
        self.full_sensor_range = self.range[0]
        if self.sensor_type == "accelerometer" and self.range[0] > 1:
            self.high_g = True
        else:
            self.high_g = False

        self.fso = [data_basic["specs"]["scale_factor"][0] for _ in range(3)]
        self.bias = [data_basic["specs"]["bias"][0] for _ in range(3)]
        self.scale_factor = [data_basic["specs"]["scale_factor"][0] for _ in range(3)]

        self.radius_positive = 0.3  # m
        self.radius_negative = 0.3  # m

        # print(f"high limit: {self.scale_factor_high_limit}")
        # print(f"low limit: {self.scale_factor_low_limit}")
        self.moa = [data_basic["specs"]["moa"][0] for _ in range(3)]
        self.mpa = [data_basic["specs"]["mpa"][0] for _ in range(3)]
        self.sfts = [data_basic["specs"]["sfts"][0] for _ in range(3)]
        self.bts = [data_basic["specs"]["bts"][0] for _ in range(3)]
        self.hysteresis = [data_basic["specs"]["hysteresis"][0] for _ in range(3)]
        self.repeatability = [data_basic["specs"]["repeatability"][0] for _ in range(3)]
        self.accuracy = [data_basic["specs"]["accuracy"][0] for _ in range(3)]
        self.resolution = [data_basic["specs"]["resolution"][0] for _ in range(3)]
        # self.pend_axis_limit = [data_basic["specs"]["pendulous_axis_misalignment"][0] for _ in range(3)]

        self.nominal_ADC = 256000
        # dimensionless, used as a tolerance in the orthonormalization matrix.
        self.orthonormal_element_limit = 0.03  # dimensionless,
        # each non-diagonal element should be with +/- 0. each diagonal element should be within +/- of 1.
        self.offset_matrix_limits = [
            5000,
            4500,
            9000,
        ]  # ADC counts, thats 3 sigma from mean for 297 sensors.

        self.factory_tare_limits = [-0.19, 0.19]

        points = self.linearity_points + 2 * self.extra_points

        if self.digital_type == "Jewell ASCII":
            self.nist_calibration_points_array = (
                calibration_array.build_calibration_array(
                    self.range[0], points, self.sensor_type
                )
            )

            self.verification_points_array = [
                -60,
                -48,
                -36,
                -30,
                -24,
                -18,
                -14.5,
                -12,
                -9,
                -6,
                -3,
                -2.4,
                -1.8,
                -1.2,
                -1,
                -0.8,
                -0.6,
                -0.4,
                -0.2,
                0,
                0.2,
                0.4,
                0.6,
                0.8,
                1,
                1.2,
                1.8,
                2.4,
                3,
                6,
                9,
                12,
                14.5,
                18,
                24,
                30,
                36,
                48,
                60,
            ]

            self.calibration_points_array = [
                -90.0,
                -65.0,
                -60.25,
                -59.75,
                -59.25,
                -58.75,
                -58.25,
                -57.5,
                -56.5,
                -55.5,
                -54.5,
                -53.5,
                -52.5,
                -51.5,
                -50.5,
                -49.5,
                -48.5,
                -47.5,
                -46.5,
                -45.5,
                -44.5,
                -43.5,
                -42.5,
                -41.5,
                -40.5,
                -39.5,
                -38.5,
                -37.5,
                -36.0,
                -34.5,
                -33.0,
                -31.5,
                -30.0,
                -28.5,
                -27.0,
                -25.5,
                -24.0,
                -22.5,
                -21.0,
                -19.5,
                -18.0,
                -16.0,
                -14.0,
                -12.0,
                -10.0,
                -8.0,
                -6.0,
                -4.0,
                -2.0,
                -0.5,
                0.0,
                0.5,
                2.0,
                4.0,
                6.0,
                8.0,
                10.0,
                12.0,
                14.0,
                16.0,
                18.0,
                19,
                21.0,
                22.5,
                24.0,
                25.5,
                27.0,
                28.5,
                30.0,
                31.5,
                33.0,
                34.5,
                36.0,
                37.5,
                38.5,
                39.5,
                40.5,
                41.5,
                42.5,
                43.5,
                44.5,
                45.5,
                46.5,
                47.5,
                48.5,
                49.5,
                50.5,
                51.5,
                52.5,
                53.5,
                54.5,
                55.5,
                56.5,
                57.5,
                58.25,
                58.75,
                59.25,
                59.75,
                60.25,
                65.0,
                90.0,
            ]
        else:
            if self.high_g is True:
                i = 0
                while (i) < self.axes_no:
                    self.fso[i], self.range[i] = high_g_correction(
                        self.fso[i], self.range[i]
                    )
                    i = i + 1
            self.scale_factor_low_limit = data_basic["specs"]["scale_factor"][0] * (
                1 - self.scale_factor_tolerance
            )
            self.scale_factor_high_limit = data_basic["specs"]["scale_factor"][0] * (
                1 + self.scale_factor_tolerance
            )
            self.calibration_points_array = calibration_array.build_calibration_array(
                self.range[0], points, self.sensor_type
            )

        # print(self.calibration_points_array)
        self.bandwidth = data_basic["specs"]["bandwidth"]
        self.bandwidth_tolerance_low = data_basic["specs"]["bandwidth_tolerance_low"]
        self.bandwidth_tolerance_high = data_basic["specs"]["bandwidth_tolerance_high"]

        self.test_bias, self.report_bias = test_identifier(
            data_basic["tests"]["test_bias"]
        )
        self.test_linearity, self.report_linearity = test_identifier(
            data_basic["tests"]["linearity"]
        )
        self.test_pend_axis, self.report_pend_axis = test_identifier(
            data_basic["tests"]["test_pend_axis"]
        )
        self.test_repeatability, self.report_repeatability = test_identifier(
            data_basic["tests"]["test_rptblty"]
        )
        self.test_hysteresis, self.report_hysteresis = test_identifier(
            data_basic["tests"]["test_hystrs"]
        )
        self.test_resolution, self.report_resolution = test_identifier(
            data_basic["tests"]["test_rsltn"]
        )
        self.test_temp, self.report_temp = test_identifier(
            data_basic["tests"]["test_over_temp"]
        )
        self.test_temp_sensor, self.report_temp_sensor = test_identifier(
            data_basic["tests"]["test_temp_sensor"]
        )
        self.test_sfts, self.report_sfts = test_identifier(
            data_basic["tests"]["test_sfts"]
        )
        self.test_bts, self.report_bts = test_identifier(
            data_basic["tests"]["test_bts"]
        )
        self.tare, self.report_tare = test_identifier(data_basic["tests"]["tare"])
        self.renormalize, self.report_renormalize = test_identifier(
            data_basic["tests"]["renormalize"]
        )
        self.nist_cal, self.report_nist_cal = test_identifier(
            data_basic["tests"]["nist_cal"]
        )

        # self.test_hysteresis = False  # only for debugging

        self.test_input_current, self.report_input_current = test_identifier(
            data_basic["tests"]["test_input_current"]
        )
        self.test_bandwidth, self.report_bandwidth = test_identifier(
            data_basic["tests"]["test_bandwidth"]
        )
        self.test_functional_voltage, self.report_function_voltage = test_identifier(
            data_basic["tests"]["voltage_test"]
        )
        self.mount = data_basic["tests"]["tare"]
        self.serial_protocol = "RS485"


def test_identifier(string: str) -> list[bool]:
    """a simple function for mapping the string from the API to a list of bools used by the software.

    Args:
        string (str): _description_

    Returns:
        list[bool]: _description_
    """
    if string == "Test Only":
        return True, False
    elif string == "Test and Report":
        return True, True
    else:
        return False, False


def high_g_correction(full_scale_output: float, sensor_range: float) -> list[float]:
    """reset range for 2g ranges, anything over 2 will have to have data entered manually.

    Args:
        full_scale_output (float): _description_
        sensor_range (float): _description_

    Returns:
        list[float]: _description_
    """
    full_scale_output = full_scale_output / sensor_range
    adjusted_sensor_range = 1
    return full_scale_output, adjusted_sensor_range
