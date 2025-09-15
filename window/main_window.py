import sys
import logging
import os
import datetime
import time
import shutil
from network import get_specs
from network import api_calls
from system import settings
from PyQt5 import QtWidgets, uic
from window import SBT_window


def parse_info(self) -> tuple [list, str]:
    """Takes the info entered by the user and determins the model number of the unit 
    Returns:
        list: the model number of the unit seperated by the dashes
    """
    settings.work_order = str(self.work_order_le.text())
    logging.info(f"Entered work order: {settings.work_order}")
    if settings.work_order != '':
        work_order, sales_order, customer, settings.work_order_part_no, settings.qty = api_calls.get_work_order(self.work_order_le.text())
        part_no = settings.work_order_part_no.strip()
        logging.info(f"Aquired part number: {part_no} from work order")
        self.part_number_le.setText(settings.work_order_part_no.strip())
        description = str(self.description_cobo.currentText())
        logging.info(f"Aquired description number: {description} from work order")
    else:
        part_no = str(self.part_number_le.text())
        logging.info(f"Entered part number: {part_no}")
        description = str(self.description_cobo.currentText())
        logging.info(f"Entered description number: {description}")
    if part_no != '':
        try: 
            model = settings.ruby_conversion_chart[part_no]
            desc = model.split("-") #JMHI-200-1-L-30
            logging.info(f"Model info returning: {model}")
            logging.info(f"Desc info returning: {desc}")
        except KeyError:
            settings.error_message(f"Part number: {part_no} not found!\n Attempting to try the entered discription")
            desc = description.split("-") #JMHI-200-1-L-30
            model = description
            logging.info(f"Model info returning: {model}")
            logging.info(f"Desc info returning: {desc}")
        except Exception as e:
            print(f"An unknown error: {e} has occured")
            logging.info(f"An unknown error: {e} has occured")
    elif description != '':
            desc = description.split("-") #JMHI-200-1-L-30
            model = description
    else:
        desc = ['']
        model = ''
    return desc, model

class Main_Window(QtWidgets.QMainWindow):
    def __init__(self):
        super(Main_Window, self).__init__()
        # get the path to the ui file
        print(settings.WINDOWS_BASE)
        logging.info(settings.WINDOWS_BASE)
        ui_file = os.path.join(settings.WINDOWS_BASE, "main_window.ui")
        # load the ui file
        uic.loadUi(ui_file, self)
        
        # PUSH BUTTONS
        ############################################################################
        self.first_assy_pb = self.findChild(QtWidgets.QPushButton, "first_assy_pb")
        self.first_assy_pb.clicked.connect(self.first_assy)

        self.cover_assy_pb = self.findChild(QtWidgets.QPushButton, "cover_assy_pb")
        self.cover_assy_pb.clicked.connect(self.cover_assy)

        self.final_assy_pb = self.findChild(QtWidgets.QPushButton, "final_assy_pb")
        self.final_assy_pb.clicked.connect(self.final_assy)

        self.calibration_pb = self.findChild(QtWidgets.QPushButton, "calibration_pb")
        self.calibration_pb.clicked.connect(self.calibration)

        self.create_label_pb = self.findChild(QtWidgets.QPushButton, "create_label_pb")
        self.create_label_pb.clicked.connect(self.create_label)

        self.program_pb = self.findChild(QtWidgets.QPushButton, "program_pb")
        self.program_pb.clicked.connect(self.program)

        self.SBT_pb = self.findChild(QtWidgets.QPushButton, "install_SBT_pb")
        self.SBT_pb.clicked.connect(self.install_SBT)

        self.help_pb = self.findChild(QtWidgets.QPushButton, "help_pb")
        self.help_pb.clicked.connect(self.help)

        self.exit_pb = self.findChild(QtWidgets.QPushButton, "exit_pb")
        self.exit_pb.clicked.connect(self.exit)
        ############################################################################

        # LINE EDITS
        ############################################################################
        self.part_number_le = self.findChild(QtWidgets.QLineEdit, "part_number_le")
        self.work_order_le = self.findChild(QtWidgets.QLineEdit, "work_order_le")
        if settings.work_order_part_no != '':
            self.work_order_le.setText(settings.work_order.strip())
            self.part_number_le.setText(settings.work_order_part_no.strip())
            self.work_order_le.setEnabled(False)
            self.part_number_le.setEnabled(False)
        ############################################################################

        # CHECK BOXES
        ############################################################################

        ############################################################################

        # TEXT EDITS
        ############################################################################

        ############################################################################

        # COMBO BOXES
        ############################################################################
        self.description_cobo = self.findChild(QtWidgets.QComboBox, "description_cobo")
        ############################################################################

        #disable the program digital ruby option for analog units
        if settings.work_order_part_no != '':
            #specs = get_specs.mems_specs(settings.work_order_part_no)
            #description = specs.model_no
            description = settings.ruby_conversion_chart[settings.work_order_part_no.strip()]
            if "JDS" not in description:
                self.program_pb.setEnabled(False)
        self.show()

    def first_assy(self):
        """Opens the appropriate power point for assembling a unit of the specified model number"""
        #specs = get_specs.mems_specs(self.part_number_le)
        desc, model_number = parse_info(self) #JMHI-200-1-L-30
        if desc == ['']:
            settings.error_message("You have not selected an option")
            return 
        range = ''
        if str(desc[3]) == 'L':
            output = "4-20mA"
        elif str(desc[3]) == 'S':
            output = "0-5V"
        elif str(desc[3]) == 'D':
            output = "5V"
        if int(desc[1]) == 100:
            axis_no = 'Single'
        elif int(desc[1]) == 200:
            axis_no = 'Dual'
        elif int(desc[1]) == 300:
            axis_no = 'Tri'
        if str(desc[0]) == 'JMHA':
            if float(desc[4]) == 10.0:
                range = '10g '
            elif float(desc[4]) == 4.0:
                range = '4g '
        folder_name = f"{axis_no}-Axis Assembly"
        file_name = f"{axis_no}-axis {range}{output} RUBY Assembly.pptx"
        try:
            file_path = os.path.join(settings.POWER_BASE, folder_name)
            os.startfile(os.path.join(file_path, file_name))
        except Exception:
            settings.error_message("Cam has not created a power point for this unit, tell him to do it")
        return 
    
    def cover_assy(self):
        """Opens the appropriate power point for assembling the cover for a unit of the specified model number"""
        desc, model_number = parse_info(self) #JMHI-200-1-L-30
        print(f"desc: {desc}")
        if desc == ['']:
            settings.error_message("You have not selected an option")
            return 
        if int(desc[2]) == 1:
            connector_type = "DB9"
        elif int(desc[2]) == 4:
            connector_type = "M12"

        file_name = f"{connector_type} RUBY Cover Assembly.pptx"
        try:
            os.startfile(os.path.join(settings.POWER_BASE, file_name))
        except Exception:
            settings.error_message("Cam has not created a power point for this unit, tell him to do it")
            return
        return
    
    def calibration(self):
        """Opens the appropriate excel sheet for calibrating a unit of the specified model number"""
        desc, model_number = parse_info(self) #JMHI-200-1-L-30
        if desc == ['']:
            settings.error_message("You have not selected an option")
            return 
        unit_range = str(desc[4])
        if str(desc[0]) == 'JMHA':
            unit_range = f"{unit_range}g"
        file_name = f"RUBY {str(desc[3])} {unit_range}.xlsx"
        try:
            os.startfile(os.path.join(settings.EXCEL_BASE, file_name))
        except Exception:
            print(file_name)
            settings.error_message("Cam has not created a cal sheet for this unit, tell him to do it")
            return
        return
    
    def create_label(self):
        """Creates a label for the specified work order"""
        if self.work_order_le == '':
            settings.error_message("A work order must have been selected to print labels")
            return
        units = 0
        desc, model_number = parse_info(self) #JMHI-200-1-L-30
        if desc == ['']:
            settings.error_message("You have not selected an option")
            return 
        if int(desc[1]) == 100:
            axis_no = 'x'
        else:
            axis_no = 'xy'

        printed_before = False
        for file in os.listdir(settings.LABEL_BASE):
            if file == f"{settings.work_order}.csv":
                print_date = time.ctime(os.path.getctime(os.path.join(settings.LABEL_BASE, f"{settings.work_order}.csv")))
                settings.error_message(f"labels for this job have already been printed on {print_date}, please double check all information and remove original file if required:\n {settings.LABEL_BASE}")
                printed_before = True
        if printed_before is False:
            week_of_the_year = datetime.date.today().isocalendar().week
            year = datetime.date.today().isocalendar().year
            start_number = api_calls.get_RUBY_label_current_number_v2(year, week_of_the_year, settings.qty, settings.work_order_part_no, settings.work_order)
            file = os.path.join(settings.LABEL_BASE, f"{settings.work_order}.csv")
            with open(file, "a") as write_file:
                    write_file.write('part_number, model_number, serial_number, matrix_text, image_path, ROHS_image, CE_image\n')
            while units < settings.qty:
                cur_unit_num = units + start_number
                num_digits = 5 - len(str(cur_unit_num))
                num = "0" * num_digits
                num = num + str(cur_unit_num)
                serial_number = f"{datetime.date.today().year}W{week_of_the_year}-{num}"
                for key, value in settings.ruby_conversion_chart.items():
                    if value == model_number:
                        part_number = key
                matrix = part_number + "," + model_number + "," + serial_number
                with open(file, "a") as write_file:
                    write_file.write(
                        f'{part_number},{model_number},{serial_number},"{matrix}",{axis_no},RoHS,ce-mark-thumbnail\n'
                        f'{part_number},{model_number},{serial_number},"{matrix}"\n'
                    )
                logging.info(f'Created label using the following info: {part_number},{model_number},{serial_number},"{matrix}",{axis_no},RoHS,ce-mark-thumbnail')
                units += 1
            shutil.copy(file, os.path.join(settings.PRINT_BASE, f"{settings.work_order}.csv"))
            settings.message("Print sucessfull!")
        self.create_label_pb.setEnabled(False)
        return
    
    def install_SBT(self):
        """Launch the install_SBT window."""
        print("you clicked the install_SBT button")
        logging.info("opening the install_SBT_window")
        self.install_SBT_app = SBT_window.SBT_Window()
        self.install_SBT_app.show()
        return
    
    def final_assy(self):
        """Opens a power point that containins the instructions for assembling the ruby cover to base"""
        file_name = "RUBY Final Assembly.pptx"
        try:
            os.startfile(os.path.join(settings.POWER_BASE, file_name))
        except Exception:
            settings.error_message("Cam has not created a power point for this part, tell him to do it")
            return
        return
    
    def program(self):
        """Opens a power point that containins the instructions for programing the digital ruby"""
        file_name = "Digital RUBY Programing.pptx"
        try:
            os.startfile(os.path.join(settings.POWER_BASE, file_name))
        except Exception:
            settings.error_message("Cam has not created a power point for this part, tell him to do it")
            return
        return

    def help(self):
        """Launch the help window."""
        settings.help_message(f"Please click on the link to a video tutorial for further instruction: {settings.MAIN_HELP_LINK}", "Main")
        return
    
    def exit(self):
        """Exit the program
        Returns:
            KeyboardInterrupt: exit the window and exit the program on close of this window
        """
        self.close()
        return KeyboardInterrupt
    

    
def start_main_window():
    app = QtWidgets.QApplication(sys.argv)
    window = Main_Window()  # noqa: F841
    app.exec_()