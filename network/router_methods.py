import os
import logging
import sys
import datetime
from system import settings


def get_file()-> str:
    files = os.listdir(settings.METHODS_BASE)
    for file in files:
        if file == f"{settings.work_order}.csv":
            file = os.path.join(settings.METHODS_BASE, file)
    return file


def get_signature_info()-> str:
    current_time = datetime.datetime.today()
    user = settings.user
    stamp = f"{current_time},{user}"
    return stamp


def get_wo_status()-> str:
    file = get_file()
    status = f"No records found for {settings.work_order}, please Print Labels to generate a work order"
    last_record = []
    with open(file, "r") as read_file:
        file_data = read_file.readlines()
        for line in file_data:
            record = line.split(",")
            if record[0] != "":
                last_record = record
    status = f"The most recent update for {settings.work_order} was on {last_record[2]} which updated sn: {last_record[0]} to status: {last_record[1]}"
    return status


def get_sn_status(sn:str = "")-> str:
    status = "Print Labels"
    file = get_file()
    with open(file, "r") as read_file:
        file_data = read_file.readlines()
        for line in file_data:
            if sn in line:
                record = line.split(",")
                status = record[1]
    return status


def update_sn_status(sn:str = "", status:str = "First Assembly"):
    print(f"sn: {sn}, work_order: {settings.work_order}")
    if sn == "":
        sn = settings.work_order
    file = get_file()
    with open(file, "a") as write_file:
        write_file.write(f"\n{sn},{status},{get_signature_info()}")
    return


def check_create_work_order_tracker()-> str:
    status = "Not found: Panic! jk, just find Cam he probably broke it"
    files = os.listdir(settings.METHODS_BASE)
    method_found_for_work_order = False
    for file in files:
        if file == f"{settings.work_order}.csv":
            method_found_for_work_order = True
            status = get_wo_status()
            break
    if method_found_for_work_order is False:
        os.path.join(settings.METHODS_BASE,f"{settings.work_order}.csv",)
        status = "Print Labels"
    return status