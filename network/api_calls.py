import socket
import os
import logging
import requests
import contextlib
import pandas 
import openpyxl

from dataclasses import dataclass

import system.settings as settings


@dataclass
class Response:
    success: bool
    status_code: int
    data: any
    error: str | None


class APIHandler:
    def __init__(
        self,
        bearer_type: str = "JWT",
        base_url: str = settings.API_URL,
        login_url: str = "token/login/",
        refresh_url: str = "token/refresh/",
        login_email: str = '', 
        login_pass: str = '', 
    ) -> None:
        self.access_token = None
        self.refresh_token = None
        self.bearer_type = bearer_type
        self.base_url = base_url
        self.refresh_url = refresh_url
        self.login_url = login_url
        self.login_email = login_email
        self.login_pass = login_pass
        #self.login()

    def login(self) -> bool:
        response = requests.post(f"{self.base_url}/{self.login_url}", json={"email": self.login_email, "password": self.login_pass}, headers={"Content-Type": "Application/json"})
        print(response.status_code)
        if response.status_code > 299:
            return False
        tokens = response.json()
        self.access_token = tokens["access"]
        self.refresh_token = tokens["refresh"]
        return True

    def update_access_token(self) -> bool:
        response = requests.post(
            f"{self.base_url}/{self.refresh_url}",
            json={"refresh": self.refresh_token},
            headers={"Content-Type": "Application/json"},
        )
        if response.status_code > 299:
            return False
        token = response.json()
        self.access_token = token["access"]
        return True

    def get(self, url: str) -> Response:
        response = requests.get(
            f"{self.base_url}/{url}",
            headers={"authorization": f"{self.bearer_type} {self.access_token}"},
        )
        print(f"responce status code: {response.status_code}")
        if response.status_code == 401:
            with contextlib.suppress(Exception):
                temp = response.json()
                if "detail" in temp:
                    return Response(False, 401, f"Unauthorized: {temp['detail']}")
            if not self.update_access_token() and not self.login():
                return Response(
                    False,
                    401,
                    None,
                    "Unauthorized: Failed to refresh access token or login",
                )
            response = requests.get(
                f"{self.base_url}/{url}",
                headers={"authorization": f"{self.bearer_type} {self.access_token}"},
            )
        if response.status_code > 299:
            return Response(False, response.status_code, None, response.text)
        return Response(True, 200, response.json(), None)

    def post(self, url: str, data: dict) -> Response:
        response = requests.post(
            f"{self.base_url}/{url}",
            json=data,
            headers={
                "Content-Type": "application/json",
                "authorization": f"{self.bearer_type} {self.access_token}",
            },
        )
        if response.status_code == 401:
            with contextlib.suppress(Exception):
                temp = response.json()
                if "detail" in temp:
                    return Response(False, 401, None, f"Unauthorized: {temp['detail']}")
            if not self.update_access_token() and not self.login():
                return Response(
                    False,
                    401,
                    None,
                    "Unauthorized: Failed to refresh access token or login",
                )
            response = requests.post(
                f"{self.base_url}/{url}",
                json=data,
                headers={
                    "Content-Type": "application/json",
                    "authorization": f"{self.bearer_type} {self.access_token}",
                },
            )
        if response.status_code > 299:
            return Response(False, response.status_code, None, response.text)
        return Response(True, 200, response.json(), None)

    def update(self, url: str, data: dict) -> Response:
        response = requests.put(
            f"{self.base_url}/{url}",
            json=data,
            headers={
                "Content-Type": "Application/json",
                "authorization": f"{self.bearer_type} {self.access_token}",
            },
        )
        if response.status_code == 401:
            with contextlib.suppress(Exception):
                temp = response.json()
                if "detail" in temp:
                    return Response(False, 401, None, f"Unauthorized: {temp['detail']}")
            if not self.update_access_token() and not self.login():
                return Response(
                    False,
                    401,
                    None,
                    "Unauthorized: Failed to refresh access token or login",
                )
            response = requests.put(
                f"{self.base_url}/{url}",
                json=data,
                headers={
                    "Content-Type": "Application/json",
                    "authorization": f"{self.bearer_type} {self.access_token}",
                },
            )
        if response.status_code > 299:
            return Response(False, response.status_code, None, response.text)
        return Response(True, 200, response.json(), None)


def get_stage_configuration() -> dict:
    """get the stage configuration from the api

    Returns:
        str: unique stage configuration based on computer host name.
    """

    api_handler = APIHandler()

    stage_configuration_response = api_handler.get(
        f"stage_configuration/?computer_name={socket.gethostname()}"
    )

    if stage_configuration_response.status_code == 200:
        stage_configuration_data = stage_configuration_response.data[-1]
    else:
        stage_configuration_data = {}
    return stage_configuration_data


def get_stage_name() -> str:
    """get the stage name from the api

    Returns:
        str: unique stage name based on computer host name.
    """

    api_handler = APIHandler()

    stage_configuration_response = api_handler.get(
        f"stage_configuration/?computer_name={socket.gethostname()}"
    )
    # print(stage_configuration.data)

    if stage_configuration_response.status_code == 200:
        stage_configuration_data = stage_configuration_response.data[-1]
        stage_name = stage_configuration_data["stage_name"]
    else:
        stage_name = "UNKNOWN"
    return stage_name


def get_equipment_on_stage(stage_name: str) -> list[dict]:
    """get all equipment that is on the stage.

    Args:
        stage_name (str): unique stage name used for controlling where things are and which equipment is active.

    Returns:
        list[dict]: list of dicts for all asset info. includes cal info.
    """

    # assets_url = urljoin(settings.API_URL, "company_assets/")
    # assets = requests.get(assets_url, params={"location": stage_name})

    api_handler = APIHandler()

    assets = api_handler.get(f"company_assets/?location={stage_name}")

    # print(assets.status_code)

    return assets.data


def get_basic_data(part_no: str) -> dict:
    """get basic calibration/test data for a given part number from the api.

    Args:
        part_no (str): _description_

    Returns:
        dict: _description_
    """
    # specs_url = urljoin(settings.API_URL, "mems_linear_specs/")
    # specs = requests.get(specs_url, params={"part_no": part_no})

    api_handler = APIHandler()

    specs = api_handler.get(f"mems_linear_specs/?part_no={part_no}")
    # print(specs.data)
    data = specs.data[-1]
    return data


def get_part_number_definition(part_no: str) -> dict:
    """get basic calibration/test data for a given part number from the api.

    Args:
        part_no (str): _description_

    Returns:
        dict: _description_
    """
    # specs_url = urljoin(settings.API_URL, "mems_linear_specs/")
    # specs = requests.get(specs_url, params={"part_no": part_no})

    api_handler = APIHandler()

    specs = api_handler.get("mems_linear_control/?detailed=True")
    # print(specs.data)

    for record in specs.data:
        # print(record["part_no"])
        if record["part_no"] == part_no:
            return record
    return {}


def get_tests_to_preform(part_no: str) -> dict:
    """get basic calibration/test data for a given part number from the api.

    Args:
        part_no (str): _description_

    Returns:
        dict: _description_
    """
    # specs_url = urljoin(settings.API_URL, "mems_linear_test/")
    # specs = requests.get(specs_url, params={"part_no": part_no})

    api_handler = APIHandler()

    specs = api_handler.get(f"mems_linear_test/?part_no={part_no}")

    data = specs.data[-1]

    return data


def get_assets_by_location(stage: str) -> list:
    """_summary_

    Args:
        stage (str): _description_

    Returns:
        list: _description_
    """
    # specs_url = urljoin(settings.API_URL, "company_assets/")

    # specs = requests.get(specs_url, params={"location": stage})

    # specs = specs.json()

    api_handler = APIHandler()

    specs_url = api_handler.get(f"company_assets/?location={stage}")
    # print(specs_url.data)

    return specs_url.data


def create_unit_id_for_sensor(
    part_no: str,
    test_index: str,
    serial_no: str,
    rma_no: str,
) -> str:
    """table needs to be made

    Args:
        part_no (str): _description_
        work_order (str): _description_
        serial_no (str): _description_
        sales_order (str): _description_
        name (str): who initiated the test
        assets (list): list of asset names used for calibration

    Returns:
        str: test index number
    """
    api_handler = APIHandler()

    response = api_handler.get("mems_linear_unit_id_log/")

    data = {
        "unit_id": response.data[-1]["unit_id"] + 1,
        "part_no": part_no,
        "test_index": test_index,
        "serial_no": serial_no,
        "rma_no": rma_no,
    }

    response = api_handler.post("mems_linear_unit_id_log/", data=data)

    response = api_handler.get("mems_linear_unit_id_log/")

    # print(response.data[-1])

    return response.data[-1]["unit_id"]  # response["unit_id"]


def get_test_index(
    part_no: str,
    work_order: str,
    sales_order: str,
    customer: str,
    name: str,
    assets: list,
    stage_name: str,
) -> int:
    """the table needs to be made...

    Args:
        part_no (str): _description_
        work_order (str): _description_
        sales_order (str): _description_
        customer (str): _description_
        name (int): pk for the User field where user matches email.
        assets (list): _description_

    Returns:
        int: _description_
    """

    api_handler = APIHandler()

    response = api_handler.get("mems_linear_test_executive/")
    initial_data = response.data[-1]

    data = {
        "test_index": initial_data["id"],
        "part_no": part_no,
        "work_order": work_order,
        "customer": customer,
        "sales_order": sales_order,
        "station": stage_name,
        "user": 2,
        "part_no_rev": "1",
        "test_result": "Fail",
        "assets": assets,
    }

    response = api_handler.post("mems_linear_test_executive/", data=data)

    # print(response.status_code)
    # api_handler = APIHandler()

    response = api_handler.get("mems_linear_test_executive/")
    data = response.data[-1]

    return data["id"]


def get_filepath_base(sensor_type: str) -> str:
    return ""


def get_work_order(work_order: str) -> tuple[str, str, str]:
    """get work order data from M2M API

    Args:
        work_order (str): _description_

    Returns:
        tuple[str, str, str]: _description_

        # http://192.168.3.11/m2mapi/RMA/11410
        # http://192.168.3.11/m2mapi/ShopFloorManager/00GEM-0000
    """

    api_handler = APIHandler(base_url=settings.M2M_API_URL)

    work_order_data = api_handler.get(f"ShopFloorManager/{work_order}")

    work_order_data = work_order_data.data

    # print(work_order_data)

    if work_order_data == []:
        return ("Not found", "", "", "")

    else:

        logging.info(work_order_data)

        return (
            work_order_data["fjobno"],
            work_order_data["fsono"],
            work_order_data["fcompany"],
            work_order_data["fpartno"].strip(),
            work_order_data["fquantity"]
        )


def get_unit_id(part_no: str, serial_no: str, rma_no: str) -> int:
    """_summary_

    Args:
        part_no (str): _description_
        serial_no (str): _description_
        rma_no (str): _description_

    Returns:
        int: _description_
    """
    api_handler = APIHandler()

    unit_id_log_data = api_handler.get(
        f"mems_linear_unit_id_log/?part_no={part_no}&serial_no={serial_no}&rma_no={rma_no}"
    )

    unit_id_log_data = unit_id_log_data.data
    logging.info(unit_id_log_data)
    for item in unit_id_log_data:
        if (
            item["part_no"] == str(part_no)
            and item["serial_no"] == str(serial_no)
            and item["rma_no"] == str(rma_no)
        ):
            return item

    return {}


def write_linearity_calibration_data(
    unit_id: int,
    axis_index: str,
    temp_index: int,
    cycle_index: int,
    reference: float,
    plate_temp: float,
    x_output: float,
    y_output: float,
    z_output: float,
    unit_temp: float,
) -> None:
    """_summary_

    Args:
        unit_id (int): _description_
        axis_index (str): _description_
        temp_index (int): _description_
        cycle_index (int): _description_
        reference (float): _description_
        plate_temp (float): _description_
        x_output (float): _description_
        y_output (float): _description_
        z_output (float): _description_
        unit_temp (float): _description_
    """

    api_handler = APIHandler()

    data = {
        "unit_id": unit_id,
        "axis_index": axis_index,
        "temp_index": temp_index,
        "cycle_index": cycle_index,
        "reference": reference,
        "plate_temp": plate_temp,
        "x_output": x_output,
        "y_output": y_output,
        "z_output": z_output,
        "unit_temp": unit_temp,
    }
    api_handler.post("mems_linear_thermal_data/", data=data)

    return


def write_factory_tare_data(
    unit_id: int,
    x_output: float,
    y_output: float,
    z_output: float,
) -> None:
    """_summary_

    Args:
        unit_id (int): _description_
        x_output (float): _description_
        y_output (float): _description_
        z_output (float): _description_
    """

    static_table = "mems_linear_tare_data/"

    api_handler = APIHandler()

    data = {
        "unit_id": unit_id,
        "x_output": x_output,
        "y_output": y_output,
        "z_output": z_output,
    }

    response = api_handler.post(static_table, data=data)

    logging.info(response.status_code)
    # logging.info(response.error)
    # logging.info(x_output)
    # logging.info(y_output)
    # logging.info(z_output)

    return


def write_static_calibration_data(
    unit_id: int,
    axis_index: str,
    output_up: float = 0.0,
    output_down: float = 0.0,
    pendulous_left: float = 0.0,
    pendulous_right: float = 0.0,
    bandwidth: float = 0.0,
    impedance: float = 0.0,
    pos_input_voltage: float = 0.0,
    neg_input_voltage: float = 0.0,
    unit_output: float = 0.0,
    angle_in_g: float = 0.0,
) -> None:
    """_summary_

    Args:
        unit_id (int): _description_
        axis_index (str): _description_
        output_up (float): _description_
        output_down (float): _description_
        pendulous_left (float): _description_
        pendulous_right (float): _description_
        bandwidth (float, optional): _description_. Defaults to 0.0.
        impedance (float, optional): _description_. Defaults to 0.0.
    """

    api_handler = APIHandler()

    data = {
        "unit_id": unit_id,
        "axis_index": axis_index,
        "output_up": output_up,
        "output_down": output_down,
        "pendulous_left": pendulous_left,
        "pendulous_right": pendulous_right,
        "bandwidth": bandwidth,
        "impedance": impedance,
        "pos_input_voltage": pos_input_voltage,
        "neg_input_voltage": neg_input_voltage,
        "unit_output": unit_output,
        "angle_in_g": angle_in_g,
    }

    api_handler.post("mems_linear_static_data/", data=data)
    return


def write_calibration_metrics(
    unit_id: int,
    axis_index: str,
    cycle_index: int,
    temp_index: int,
    scale_factor: float,
    moa: float,
    mpa: float,
    bias: float,
    sfts: float = 0.0,
    bts: float = 0.0,
    linearity: float = 0.0,
) -> None:
    """write the calibration metrics to the api for easy reporting.d

    Args:
        unit_id (int): _description_
        axis_index (str): _description_
        cycle_index (int): _description_
        temp_index (int): _description_
        scale_factor (float): _description_
        moa (float): _description_
        mpa (float): _description_
        bias (float): _description_
        sfts (float, optional): _description_. Defaults to 0.0.
        bts (float, optional): _description_. Defaults to 0.0.
    """
    api_handler = APIHandler()

    data = {
        "unit_id": unit_id,
        "axis_index": axis_index,
        "cycle_index": cycle_index,
        "temp_index": temp_index,
        "scale_factor": scale_factor,
        "moa": moa,
        "mpa": mpa,
        "bias": bias,
        "sfts": sfts,
        "bts": bts,
        "linearity": linearity,
    }

    api_handler.post("mems_linear_calibration_metrics/", data=data)
    return


def write_jdx_tumble_calibration_data(
    unit_id: int,
    reference: float,
    x_output: float,
    y_output: float,
    z_output: float,
) -> None:
    """_summary_

    Args:
        unit_id (int): _description_
        axis_index (str): _description_
        temp_index (int): _description_
        cycle_index (int): _description_
        reference (float): _description_
        plate_temp (float): _description_
        x_output (float): _description_
        y_output (float): _description_
        z_output (float): _description_
        unit_temp (float): _description_
    """
    static_table = "mems_linear_tumble_data/"

    api_handler = APIHandler()
    # api_handler.post("mems_linear_thermal_data/", data=data)

    data = {
        "unit_id": unit_id,
        "reference": reference,
        "x_output": x_output,
        "y_output": y_output,
        "z_output": z_output,
    }

    # {"unit_id": 2147483647, "x_output": 0, "y_output": 0, "z_output": 0}
    response = api_handler.post(static_table, data=data)

    logging.info(response.status_code)
    logging.info(response.error)
    # logging.info(x_output)
    # logging.info(y_output)
    # logging.info(z_output)

    return


def write_jmx_high_low_power_test_data(
    unit_id: int,
    reference: float,
    x_output: float,
    y_output: float,
    z_output: float,
    positive_power: float,
    negative_power: float,
) -> None:
    """_summary_

    Args:
        unit_id (int): _description_
        reference (float): _description_
        x_output (float): _description_
        y_output (float): _description_
        z_output (float): _description_
    """
    # power_line_table = "mems_linear_power_line_cal_data/"
    # power_line_url = urljoin(settings.API_URL, power_line_table)

    data = {
        "unit_id": unit_id,
        "reference_input": reference,
        "x_output": x_output,
        "y_output": y_output,
        "z_output": z_output,
        "positive_power": positive_power,
        "negative_power": negative_power,
    }
    logging.info(data)
    # response = requests.post(power_line_url, data=data)

    api_handler = APIHandler()

    response = api_handler.post("mems_linear_power_line_cal_data/", data=data)

    logging.info(response.status_code)


def set_stage_status_as_inactive(
    stage_name: str, status: str = "Needs Operator"
) -> None:
    """_summary_

    Args:
        stage_name (str): _description_
        status (str, optional): _description_. Defaults to "Needs Operator".
    """
    api_handler = APIHandler()
    # figure out how to get the user id from who's logged in. 10/10/24

    data = {"stage_name": stage_name, "status": status}

    stage_status = api_handler.update(f"cal_stage_status/{stage_name}", data=data)
    # response = api_handler.update(f"cal_stage_status/{stage_name}/", data=data)

    logging.info(stage_status.status_code)

    return


def set_stage_status(
    stage_name: str = "err: not specified",
    part_no: str = "err: not specified",
    job_no: str = "err: not specified",
    axis: str = "err: not specified",
    cycle: int = "err: not specified",
    temperature: float = "err: not specified",
    status: str = "Needs Operator",
) -> None:
    """_summary_

    Args:
        stage_name (str): _description_
        part_no (str): _description_
        job_no (str): _description_
        axis (str): _description_
        cycle (int): _description_
        temperature (float): _description_
        status (str): _description_
    """
    api_handler = APIHandler()

    # figure out how to get the user id from who's logged in. 10/10/24

    data = {
        "stage_name": stage_name,
        "part_number": part_no,
        "job_number": job_no,
        "axis": axis,
        "cycle": cycle,
        "temperature": temperature,
        "status": status,
    }

    response = api_handler.update(f"cal_stage_status/{stage_name}/", data=data)

    logging.info(response.status_code)
    logging.info(response.error)

    return


def add_item_to_root_cause_tracker(
    part_no: str = "err: not found",
    serial_no: str = "err: not found",
    work_order: str = "err: not found",
    symptoms: str = "error: not found",
    diagnosis: str = "Auto Diagnosis: N/A",
    notes: str = "Created by ATP",
    status: str = "Open",
    creator: int = 2,
):

    data_dict = {
        "part_no": part_no,
        "serial_no": serial_no,
        "work_order": work_order,
        "symptom": symptoms,
        "diagnosis": diagnosis,
        "notes": notes,
        "status": status,
        "creator": creator,
    }

    api_handler = APIHandler()
    root_cause = api_handler.post("root_cause_tracking/", data=data_dict)
    logging.info(root_cause.status_code)


def set_success_status_in_test_executive(test_id: int, status: bool) -> None:
    """set a bool in the test executive for a given test id

    Args:
        test_id (int): _description_
    """

    return


def get_user_id(user_name: str) -> int:
    """_summary_
    Args:
        user_name (str): _description_
    Returns:
        int: _description_
    """
    api_handler = APIHandler()
    response = api_handler.get("users/")
    for user in response.data:
        if user["email"] == f"{user_name}@jewellinstruments.com":
            return user["id"]
    return 2


def is_user_in_group(user_name: str, in_group: str) -> bool:
    """_summary_
    Args:
        user_name (str): _description_
    Returns:
        int: _description_
    """
    api_handler = APIHandler()
    response = api_handler.get("users/")
    for user in response.data:
        if "@" not in user_name:
            user_name = f"{user_name}@jewellinstruments.com"
        if user["email"] == user_name:
            for group in user["groups"]:
                if group == in_group:
                    return True
    return False


def get_RUBY_label_current_number(year, week_of_the_year, number_of_units, part_number, work_order) -> int:
    api_handler = APIHandler()
    data1 = {"0", "879838", "I0PAI-0000"}
    data2 = {"serial_number": ["2025W22-00001",], "part_number": ["879838",], "work_order": ["I0PAI-0000",]}
    data3 = {0, "879838", "I0PAI-0000"}
    try:
        table_data = api_handler.get("serial_number/")
        print(f"data: {table_data}")
        print(f"data data: {table_data.data}")
    except Exception as e:
        print(f"data did not work, error: {e}")
    try:
        table_data1 = api_handler.post("serial_number/", data1)
        print(f"data1: {table_data1}")
        print(f"data1 data: {table_data1.data}")
    except Exception as e:
        print(f"data1 did not work, error: {e}")
    try:
        table_data2 = api_handler.post("serial_number/", data2)
        print(f"data2: {table_data2}")
        print(f"data2 data: {table_data2.data}")
    except Exception as e:
        print(f"data2 did not work, error: {e}")
    try:
        table_data3 = api_handler.post("serial_number/", data3)
        print(f"data3: {table_data3}")
        print(f"data3 data: {table_data3.data}")
    except Exception as e:
        print(f"data3 did not work, error: {e}")
    try: 
        table_data = table_data1.data
        print(f"Table data: {table_data}") #returns none
        current_week = table_data["current_week"] 
        current_number = table_data["current_number"]

        if current_week != week_of_the_year:
            table_data["current_week"] = current_week
            table_data["current_number"] = number_of_units
            api_handler.update("SerialNumber_serialnumbertrack", table_data) #set current_week to the week_of_the_year, set current_number to 0 
            start_number = 1
        else:
            table_data["current_number"] = current_number + number_of_units
            api_handler.update("SerialNumber_serialnumbertrack", table_data) #set current_week to the week_of_the_year, set current_number to 0 
            start_number = current_number + 1
    except Exception as e:
        print(f"Basicly the call to the api you tried earlier does not work, I am not sure why it is designed so differently from everything else, why cant I just do a get?? offical error: {e} ")
        start_number = 0
    return start_number


def get_RUBY_label_current_number_v2(year, week_of_the_year, number_of_units, part_number, work_order) -> int:
    RUBY_label_log = pandas.read_excel(os.path.join(settings.POWER_BASE, "RUBY_label_log.xlsx"))

    last_year = RUBY_label_log.iloc[0, 0]
    last_week = RUBY_label_log.iloc[0, 1]
    last_unit = RUBY_label_log.iloc[0, 2]

    print(f"last_year: {last_year}")
    print(f"last_week: {last_week}")
    print(f"last_unit: {last_unit}")

    if (last_year != year) or (last_week !=week_of_the_year):
        start_number = 1
    else:
        start_number = last_unit

    update_ruby_label_count(year, week_of_the_year, number_of_units, start_number)

    RUBY_label_log = pandas.read_excel(os.path.join(settings.POWER_BASE, "RUBY_label_log.xlsx"))
    
    new_year = RUBY_label_log.iloc[0, 0]
    new_week = RUBY_label_log.iloc[0, 1]
    new_unit = RUBY_label_log.iloc[0, 2]

    print(f"new_year: {new_year}")
    print(f"new_week: {new_week}")
    print(f"new_unit: {new_unit}")

    return start_number


def update_ruby_label_count(year, week_of_the_year, number_of_units, start_number):
    RUBY_label_log = openpyxl.load_workbook(os.path.join(settings.POWER_BASE, "RUBY_label_log.xlsx"))
    log_sheet = RUBY_label_log['Sheet1']
    log_sheet['A2'] = year
    log_sheet['B2'] = week_of_the_year
    log_sheet['C2'] = start_number + number_of_units

    RUBY_label_log.save(os.path.join(settings.POWER_BASE, "RUBY_label_log.xlsx"))
    return
