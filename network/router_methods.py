import os
import logging
import sys
import datetime
from system import settings

def get_signature_info():
    current_time = datetime.datetime.now()
    user = settings.user
    stamp = f"{current_time},{user}"
    return stamp


def create_new_work_order_tracker():
    file = os.path.join(settings.METHODS_BASE,f"{settings.work_order}.csv",)
    with open(file, "a") as write_file:
        write_file.write(f"{settings.work_order},Print Labels,{get_signature_info()}")
    return 


def get_sn_status(sn:str = settings.work_order) -> str:
    """returns the status of the specified serial number (or work order)
    Args:
        file (_type_): _description_
        sn (str, optional): The serial number of the unit. Defaults to the work order.
    Returns:
        str: status
    """
    status = "Not found: Panic! jk, just find Cam he probably broke it"
    try:
        files = os.listdir(settings.METHODS_BASE)
        for file in files:
            if file == f"{settings.work_order}.csv":
                file = os.path.join(settings.METHODS_BASE, file)
                with open(file, "r") as read_file:
                    file_data = read_file.readlines()
                    for line in file_data:
                        if sn in line:
                            record = line.split(",")
                            status = record[1]
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        error = f"\t{e} -> Line {exc_tb.tb_lineno}"
        logging.warning(error)
        print(error)

    return status


def update_sn_status(sn:str = "", status:str = "First Assembly"):
    print(f"sn: {sn}, work_order: {settings.work_order}")
    if sn == "":
        sn = settings.work_order
    files = os.listdir(settings.METHODS_BASE)
    for file in files:
        if file == f"{settings.work_order}.csv":
            file = os.path.join(settings.METHODS_BASE, file)
            with open(file, "a") as write_file:
                write_file.write(f"\n{sn},{status},{get_signature_info()}")
    return


def check_create_work_order_tracker():
    status = "Not found: Panic! jk, just find Cam he probably broke it"
    files = os.listdir(settings.METHODS_BASE)
    method_found_for_work_order = False
    for file in files:
        if file == f"{settings.work_order}.csv":
            method_found_for_work_order = True
            status = get_sn_status()
            break
    if method_found_for_work_order is False:
        create_new_work_order_tracker()
        status = "Print Labels"
    return status