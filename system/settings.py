import logging
import os
import datetime
import socket
import sys
import system.log_config as log_config
from PyQt5.QtWidgets import QMessageBox

#environ variables
Login_fail_count = 0
LOGGED_IN = False
work_order_part_no = ''
work_order = ''
qty = 0
need_to_save_info = False

#computer file variables
HOST_NAME = socket.gethostname()
HOME_PATH = os.path.expanduser("~")
__PROGRAM_NAME__ = "Ruby_Program"
EXE_BASE_PATH = "C:\\Program Files (x86)\\{0}\\{0}\\".format(__PROGRAM_NAME__)
SYST_BASE_PATH = "C:\\WINDOWS\\system32"
GIT_BASE_PATH = "C:\\Users\\cbrochu\\Documents\\GitHub"
base_path = os.getcwd()
base = ""
base = EXE_BASE_PATH if base_path == SYST_BASE_PATH else base_path
logging.info(base)
SHAKER_BASE = os.path.join(base, __PROGRAM_NAME__)
WINDOWS_BASE = base + "\window"
POWER_BASE = "X:\Engineering\Engineers Folders\Cameron Brochu\Ruby Info\Ruby Assembly"
EXCEL_BASE = "X:\Engineering\Engineers Folders\Cameron Brochu\Ruby Info\Ruby Calibration"
LABEL_BASE = "X:\Production\LabelDesigns\Brady_Print_Server_Repo_Channel_2\Print_Records"
PRINT_BASE = "X:\Production\LabelDesigns\Brady_Print_Server_Repo_Channel_2"
API_URL = "http://192.168.3.11/api"
M2M_API_URL = "http://192.168.3.11/m2mapi"


#log file info
LOG_ID = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
log_file_directory = f"{HOME_PATH}\\{HOST_NAME}\\{__PROGRAM_NAME__}_Error_Logs"
log_file_path = os.path.join(log_file_directory, f"error_log_{LOG_ID}")
LOG_DATE_TIME = "%Y%m%d%H%M%S"
LOG_LEVEL = logging.INFO
log_config.init_directory(log_file_path)

print("creating log folder")
date_time = datetime.datetime.now().strftime(LOG_DATE_TIME)
log_format = "%(asctime)s (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s"
print(f"log file is created here: {log_file_path}")

logging.basicConfig(
    filename=os.path.join(log_file_path, "error.log"),
    level=LOG_LEVEL,
    format=log_format,
    force=True,
)
logging.getLogger(__name__).addHandler(logging.StreamHandler(sys.stdout))
logging.info("logging setup correctly!")
print("logging setup correctly")


#help statements
MAIN_HELP_LINK = "link not available"
LOGIN_HELP_LINK = "link not available"
SBT_HELP_LINK = "link not available"

#popup messages (no user input)
def error_message(error_message: str):
    logging.info(f"Error message popup: {error_message}")
    dlg = QMessageBox()
    dlg.setWindowTitle("Error")
    dlg.setText(error_message)
    dlg.exec()
    return

def message(message: str):
    logging.info(f"message popup: {message}")
    dlg = QMessageBox()
    dlg.setWindowTitle("Message")
    dlg.setText(message)
    dlg.exec()
    return

def help_message(help_message: str, name: str =''):
    logging.info(f"help message popup: {help_message}")
    dlg = QMessageBox()
    dlg.setWindowTitle(f"{name} Help Message")
    dlg.setText(help_message)
    dlg.exec()
    return

ruby_conversion_chart = {
    "Part_number":"model_number",
    "02550431-1112" : "JMHA-100-1-S-0.5",
    "02550431-1113" : "JMHA-100-1-S-1.0",
    "02550431-1114" : "JMHA-100-1-S-2.0",
    "02550431-1116" : "JMHA-100-1-S-4.0",
    "02550431-1118" : "JMHA-100-1-S-10.0",
    "02550431-1122" : "JMHA-100-1-D-0.5",
    "02550431-1123" : "JMHA-100-1-D-1.0",
    "02550431-1124" : "JMHA-100-1-D-2.0",
    "02550431-1126" : "JMHA-100-1-D-4.0",
    "02550431-1128" : "JMHA-100-1-D-10.0",
    "02550431-1132" : "JMHA-100-1-L-0.5",
    "02550431-1133" : "JMHA-100-1-L-1.0",
    "02550431-1134" : "JMHA-100-1-L-2.0",
    "02550431-1136" : "JMHA-100-1-L-4.0",
    "02550431-1138" : "JMHA-100-1-L-10.0",
    "02550431-1412" : "JMHA-100-4-S-0.5",
    "02550431-1413" : "JMHA-100-4-S-1.0",
    "02550431-1414" : "JMHA-100-4-S-2.0",
    "02550431-1416" : "JMHA-100-4-S-4.0",
    "02550431-1418" : "JMHA-100-4-S-10.0",
    "02550431-1422" : "JMHA-100-4-D-0.5",
    "02550431-1423" : "JMHA-100-4-D-1.0",
    "02550431-1424" : "JMHA-100-4-D-2.0",
    "02550431-1426" : "JMHA-100-4-D-4.0",
    "02550431-1428" : "JMHA-100-4-D-10.0",
    "02550431-1432" : "JMHA-100-4-L-0.5",
    "02550431-1433" : "JMHA-100-4-L-1.0",
    "02550431-1434" : "JMHA-100-4-L-2.0",
    "02550431-1436" : "JMHA-100-4-L-4.0",
    "02550431-1438" : "JMHA-100-4-L-10.0",
    "02550431-2112" : "JMHA-200-1-S-0.5",
    "02550431-2113" : "JMHA-200-1-S-1.0",
    "02550431-2114" : "JMHA-200-1-S-2.0",
    "02550431-2116" : "JMHA-200-1-S-4.0",
    "02550431-2118" : "JMHA-200-1-S-10.0",
    "02550431-2122" : "JMHA-200-1-D-0.5",
    "02550431-2123" : "JMHA-200-1-D-1.0",
    "02550431-2124" : "JMHA-200-1-D-2.0",
    "02550431-2126" : "JMHA-200-1-D-4.0",
    "02550431-2128" : "JMHA-200-1-D-10.0",
    "02550431-2132" : "JMHA-200-1-L-0.5",
    "02550431-2133" : "JMHA-200-1-L-1.0",
    "02550431-2134" : "JMHA-200-1-L-2.0",
    "02550431-2136" : "JMHA-200-1-L-4.0",
    "02550431-2138" : "JMHA-200-1-L-10.0",
    "02550431-2412" : "JMHA-200-4-S-0.5",
    "02550431-2413" : "JMHA-200-4-S-1.0",
    "02550431-2414" : "JMHA-200-4-S-2.0",
    "02550431-2416" : "JMHA-200-4-S-4.0",
    "02550431-2418" : "JMHA-200-4-S-10.0",
    "02550431-2422" : "JMHA-200-4-D-0.5",
    "02550431-2423" : "JMHA-200-4-D-1.0",
    "02550431-2424" : "JMHA-200-4-D-2.0",
    "02550431-2426" : "JMHA-200-4-D-4.0",
    "02550431-2428" : "JMHA-200-4-D-10.0",
    "02550431-2432" : "JMHA-200-4-L-0.5",
    "02550431-2433" : "JMHA-200-4-L-1.0",
    "02550431-2434" : "JMHA-200-4-L-2.0",
    "02550431-2436" : "JMHA-200-4-L-4.0",
    "02550431-2438" : "JMHA-200-4-L-10.0",
    "02550431-3112" : "JMHA-300-1-S-0.5",
    "02550431-3113" : "JMHA-300-1-S-1.0",
    "02550431-3114" : "JMHA-300-1-S-2.0",
    "02550431-3116" : "JMHA-300-1-S-4.0",
    "02550431-3118" : "JMHA-300-1-S-10.0",
    "02550431-3122" : "JMHA-300-1-D-0.5",
    "02550431-3123" : "JMHA-300-1-D-1.0",
    "02550431-3124" : "JMHA-300-1-D-2.0",
    "02550431-3126" : "JMHA-300-1-D-10.0",
    "02550431-3128" : "JMHA-300-1-D-10.0",
    "02550431-3132" : "JMHA-300-1-L-0.5",
    "02550431-3133" : "JMHA-300-1-L-1.0",
    "02550431-3134" : "JMHA-300-1-L-2.0",
    "02550431-3136" : "JMHA-300-1-L-4.0",
    "02550431-3138" : "JMHA-300-1-L-10.0",
    "02550431-3412" : "JMHA-300-4-S-0.5",
    "02550431-3413" : "JMHA-300-4-S-1.0",
    "02550431-3414" : "JMHA-300-4-S-2.0",
    "02550431-3416" : "JMHA-300-4-S-4.0",
    "02550431-3418" : "JMHA-300-4-S-10.0",
    "02550431-3422" : "JMHA-300-4-D-0.5",
    "02550431-3423" : "JMHA-300-4-D-1.0",
    "02550431-3424" : "JMHA-300-4-D-2.0",
    "02550431-3426" : "JMHA-300-4-D-4.0",
    "02550431-3428" : "JMHA-300-4-D-10.0",
    "02550431-3432" : "JMHA-300-4-L-0.5",
    "02550431-3433" : "JMHA-300-4-L-1.0",
    "02550431-3434" : "JMHA-300-4-L-2.0",
    "02550431-3436" : "JMHA-300-4-L-4.0",
    "02550431-3438" : "JMHA-300-4-L-10.0",
    "02550433-1112" : "JMHI-100-1-S-1",
    "02550433-1113" : "JMHI-100-1-S-3",
    "02550433-1114" : "JMHI-100-1-S-14.5",
    "02550433-1116" : "JMHI-100-1-S-30",
    "02550433-1118" : "JMHI-100-1-S-60",
    "02550433-1119" : "JMHI-100-1-S-90",
    "02550433-1122" : "JMHI-100-1-D-1",
    "02550433-1123" : "JMHI-100-1-D-3",
    "02550433-1124" : "JMHI-100-1-D-14.5",
    "02550433-1126" : "JMHI-100-1-D-30",
    "02550433-1128" : "JMHI-100-1-D-60",
    "02550433-1129" : "JMHI-100-1-D-90",
    "02550433-1132" : "JMHI-100-1-L-1",
    "02550433-1133" : "JMHI-100-1-L-3",
    "02550433-1134" : "JMHI-100-1-L-14.5",
    "02550433-1136" : "JMHI-100-1-L-30",
    "02550433-1138" : "JMHI-100-1-L-60",
    "02550433-1139" : "JMHI-100-1-L-90",
    "02550433-1412" : "JMHI-100-4-S-1",
    "02550433-1413" : "JMHI-100-4-S-3",
    "02550433-1414" : "JMHI-100-4-S-14.5",
    "02550433-1416" : "JMHI-100-4-S-30",
    "02550433-1418" : "JMHI-100-4-S-60",
    "02550433-1419" : "JMHI-100-4-S-90",
    "02550433-1422" : "JMHI-100-4-D-1",
    "02550433-1423" : "JMHI-100-4-D-3",
    "02550433-1424" : "JMHI-100-4-D-14.5",
    "02550433-1426" : "JMHI-100-4-D-30",
    "02550433-1428" : "JMHI-100-4-D-60",
    "02550433-1429" : "JMHI-100-1-D-90",
    "02550433-1432" : "JMHI-100-4-L-1",
    "02550433-1433" : "JMHI-100-4-L-3",
    "02550433-1434" : "JMHI-100-4-L-14.5",
    "02550433-1436" : "JMHI-100-4-L-30",
    "02550433-1438" : "JMHI-100-4-L-60",
    "02550433-1439" : "JMHI-100-4-L-90",
    "02550433-2112" : "JMHI-200-1-S-1",
    "02550433-2113" : "JMHI-200-1-S-1",
    "02550433-2114" : "JMHI-200-1-S-14.5",
    "02550433-2116" : "JMHI-200-1-S-30",
    "02550433-2118" : "JMHI-200-1-S-60",
    "02550433-2119" : "JMHI-200-1-S-90",
    "02550433-2122" : "JMHI-200-1-D-1",
    "02550433-2123" : "JMHI-200-1-D-3",
    "02550433-2124" : "JMHI-200-1-D-14.5",
    "02550433-2126" : "JMHI-200-1-D-30",
    "02550433-2128" : "JMHI-200-1-D-60",
    "02550433-2129" : "JMHI-200-1-D-90.0",
    "02550433-2132" : "JMHI-200-1-L-1",
    "02550433-2133" : "JMHI-200-1-L-3",
    "02550433-2134" : "JMHI-200-1-L-14.5",
    "02550433-2136" : "JMHI-200-1-L-30",
    "02550433-2138" : "JMHI-200-1-L-60",
    "02550433-2139" : "JMHI-200-1-L-90",
    "02550433-2412" : "JMHI-200-4-S-1",
    "02550433-2413" : "JMHI-200-4-S-3",
    "02550433-2414" : "JMHI-200-4-S-14.5",
    "02550433-2416" : "JMHI-200-4-S-30",
    "02550433-2418" : "JMHI-200-4-S-60",
    "02550433-2419" : "JMHI-200-4-S-90",
    "02550433-2422" : "JMHI-200-4-D-1",
    "02550433-2423" : "JMHI-200-4-D-3",
    "02550433-2424" : "JMHI-200-4-D-14.5",
    "02550433-2426" : "JMHI-200-4-D-30",
    "02550433-2428" : "JMHI-200-4-D-60",
    "02550433-2429" : "JMHI-200-4-D-90.0",
    "02550433-2432" : "JMHI-200-4-L-1",
    "02550433-2433" : "JMHI-200-4-L-3",
    "02550433-2434" : "JMHI-200-4-L-14.5",
    "02550433-2436" : "JMHI-200-4-L-30",
    "02550433-2438" : "JMHI-200-4-L-60",
    "02550433-2439" : "JMHI-200-4-L-90",
    "02550444-2414" : "JMHI-200-4-S-14.5-V",
    "02550444-2416" : "JMHI-200-4-S-30-V",
    "02550444-2418" : "JMHI-200-4-S-60-V",
    "02550444-2419" : "JMHI-200-4-S-90-V",
    "02550444-2424" : "JMHI-200-4-D-14.5-V",
    "02550444-2426" : "JMHI-200-4-D-30-V",
    "02550444-2428" : "JMHI-200-4-D-60-V",
    "02550444-2429" : "JMHI-200-4-D-90.0-V",
    "02550444-2434" : "JMHI-200-4-L-14.5-V",
    "02550444-2436" : "JMHI-200-4-L-30-V",
    "02550444-2438" : "JMHI-200-4-L-60-V",
    "02550444-2439" : "JMHI-200-4-L-90-V"
}

username_table = 'usernames'

password_table = 'passwords'

#cams_temp_username_learning_tool = {
#    "employee_id" : "username",
#    "08095" : "cbrochu"
#}

#cams_temp_password_learning_tool = {
#    "username" : "password",
#    "cbrochu" : "JarjarB1nks97!"
#}