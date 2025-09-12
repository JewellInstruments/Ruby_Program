import sys
import logging
import os
import keyring
import system.settings as settings
import system.api_calls as api_calls
from PyQt5 import QtWidgets, uic, QtGui
import pandas

def calculate_resistors_in_parallel(target_resistor):
    r1 = 0
    r2 = 0
    return r1, r2

def read_data(serial_no, data):
    bias = 0
    sf = 0

    filtered_data = data[data["Serial Number"] == serial_no].head()

    row = filtered_data.tail(1)
    try:
        row_num = int(row.index[0])
    except:
        print(f"no data was found for serial number: {serial_no}, please confirm work order and serial number details are correct and the unit has been calibrated then try again")
        return "fail", "fail", "fail", "fail"
    bias = int(data.iloc[row_num,1])
    sf = int(data.iloc[row_num,2])
    bias1, bias2 = calculate_resistors_in_parallel(bias)
    sf1, sf2 = calculate_resistors_in_parallel(sf)
    return bias1, bias2, sf1, sf2

def display_resistors(resistor_dict, axis):
    #do image stuff
    picture_folder = os.path.join(settings.POWER_BASE, "SBT Install")
    if axis == 1:
        pic = "x_axis_sbt.png"
    elif axis == 2:
        pic = "xy_axis_sbt.png"
    elif axis == 3:
        pic = "xyz_axis_sbt.png"
    image_path = os.path.join(picture_folder, pic)

    #do text stuff
    text = "install the following resistors:\n"
    i=0
    print(f"list of resistors: {resistor_dict}")
    for key, value in resistor_dict.items():
        print(f"key: {key}, value: {value}")
        if i < 2:
            resistor = f"On {key} install a {value} resistor               "
            i+=1
        elif i >= 2:
            resistor = f"On {key} install a {value} resistor\n"
            i = 0
        text = text + resistor
    print(text)

    #display popup
    popup = ImagePopup(image_path, text)
    popup.exec_()
    return

class ImagePopup(QtWidgets.QDialog):
    def __init__(self, image_path, text, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Install SBT Resistors")
        self.setFixedWidth(1100)
        self.setFixedHeight(950)
        font = QtGui.QFont()
        font.setPointSize(20)
        self.setFont(font)

        # Create a layout
        layout = QtWidgets.QVBoxLayout()

        # Add image
        image_label = QtWidgets.QLabel(self)
        pixmap = QtGui.QPixmap(image_path)
        image_label.setPixmap(pixmap)
        layout.addWidget(image_label)

        # Add text
        text_label = QtWidgets.QLabel(text, self)
        layout.addWidget(text_label)

        # Set layout
        self.setLayout(layout)

class BarcodeEntryPopup(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(BarcodeEntryPopup, self).__init__(parent)
        self.barcode_label = QtWidgets.QLabel(self)
        self.barcode_label.setText("Data Matrix Value")
        self.barcode_value = QtWidgets.QLineEdit(self)
        self.go = QtWidgets.QPushButton("Go", self)
        self.go.clicked.connect(self.handleLogin)
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.barcode_label)
        layout.addWidget(self.barcode_value)
        layout.addWidget(self.go)
    def handleLogin(self):
        self.accept()


class SBT_Window(QtWidgets.QMainWindow):
    def __init__(self):
        super(SBT_Window, self).__init__()
        # get the path to the ui file
        print(settings.WINDOWS_BASE)
        logging.info(settings.WINDOWS_BASE)
        ui_file = os.path.join(settings.WINDOWS_BASE, "SBT_window.ui")
        # load the ui file
        uic.loadUi(ui_file, self)

        # PUSH BUTTONS
        ############################################################################
        self.sn_barcode_sn_pb = self.findChild(QtWidgets.QPushButton, "sn_barcode_pb")
        self.sn_barcode_sn_pb.clicked.connect(self.barcode_sn)

        self.sn_barcode_wo_pb = self.findChild(QtWidgets.QPushButton, "wo_barcode_pb")
        self.sn_barcode_wo_pb.clicked.connect(self.barcode_wo)
        
        self.start_pb = self.findChild(QtWidgets.QPushButton, "start_pb")
        self.start_pb.clicked.connect(self.start)

        self.help_pb = self.findChild(QtWidgets.QPushButton, "help_pb")
        self.help_pb.clicked.connect(self.help)

        self.exit_pb = self.findChild(QtWidgets.QPushButton, "exit_pb")
        self.exit_pb.clicked.connect(self.exit)
        ############################################################################
        
        # LINE EDITS:
        ############################################################################
        self.serial_number_le = self.findChild(QtWidgets.QLineEdit, "serial_number_le")
        self.work_order_le = self.findChild(QtWidgets.QLineEdit, "work_order_le")
        ############################################################################
        self.show()



    def barcode_sn(self):
        """Allows the user to scan their keycard to log in if they have logged in once before
        """
        dialog = BarcodeEntryPopup(self)
        if dialog.exec_():
            response = dialog.barcode_value.text()
            matrix = response.split(",")
            desc = matrix[1]
            logging.info(f"The user scanned the barcode containing: {response} as the user info")
            logging.info(f"The scanned response resulted in the following discription: {desc}")
        self.serial_number_le.setText(desc)
        return
    
    def barcode_wo(self):
        """Allows the user to scan a barcode on a production floor traveler to get the work order
        """
        dialog = BarcodeEntryPopup(self)
        if dialog.exec_():
            response = dialog.barcode_value.text()
            if response == "":
                return
            else:
                try: 
                    response = response[1:].strip()
                    logging.info(f"The user scanned the barcode containing: {response} as the work order info")
                    self.work_order_le.setText(response)
                except Exception as e:
                    print(f"an unknown error: {e} has occured") 
                    logging.info(f"an unknown error: {e} has occured")
        return
    

    def start(self):
        """_summary_
        This function checks the provided login information and if true passes the entered info to the next window
        """
        logging.info("SBT start button pushed")
        if self.work_order_le != "":
            if self.work_order_le.text() != '':
                try:
                    settings.work_order, sales_order, customer, settings.work_order_part_no, settings.qty = api_calls.get_work_order(self.work_order_le.text())
                    logging.info(f"workorder: {settings.work_order} found")
                except Exception as e:
                    logging.info(f"login_window.py Error: {e}")
                    settings.error_message("Failed to find work order, work order will not be overwritten")
        desc = settings.ruby_conversion_chart[settings.work_order_part_no.strip()]
        description = desc.split("-")
        #print(f"description: {description}")
        if description == ['']:
            settings.error_message("You have not selected an option")
            return 
        unit_range = str(description[4])
        if str(description[0]) == 'JMHA':
            unit_range = f"{unit_range}g"
        file_name = f"RUBY {str(description[3])} {unit_range}.xlsx"
        try:
            file = os.path.join(settings.EXCEL_BASE, file_name)
        except Exception:
            print(file_name)
            settings.error_message("Error: Calibration data file cannot be found!")
            return
        serial_no = str(self.serial_number_le.text())
        axis = int(description[1][0])
        resistors_dict = {}
        if axis == 3:
            z_data = pandas.read_excel(file, sheet_name="Z Axis")
            R27, R28, R25, Runknown2 = read_data(serial_no, pandas.DataFrame(z_data))
            if R27 == "fail":
                settings.error_message(f"no data was found for serial number: {serial_no}, please confirm work order and serial number details are correct and the unit has been calibrated then try again")
                return
            resistors_dict['R27'] = R27*1000
            resistors_dict['R28'] = R28*1000
            resistors_dict['R25'] = R25*1000
            resistors_dict['Runknown2'] = Runknown2*1000
        if axis >= 2:
            y_data = pandas.read_excel(file, sheet_name="Y Axis")
            R20, R21, R15, R18 = read_data(serial_no, pandas.DataFrame(y_data))
            if R20 == "fail":
                settings.error_message(f"no data was found for serial number: {serial_no}, please confirm work order and serial number details are correct and the unit has been calibrated then try again")
                return
            resistors_dict['R20'] = R20*1000
            resistors_dict['R21'] = R21*1000
            resistors_dict['R15'] = R15*1000
            resistors_dict['R18'] = R18*1000
        if axis >= 1: 
            x_data = pandas.read_excel(file, sheet_name="X Axis")
            R13, R14, R8, R11 = read_data(serial_no, pandas.DataFrame(x_data))
            if R13 == "fail":
                settings.error_message(f"no data was found for serial number: {serial_no}, please confirm work order and serial number details are correct and the unit has been calibrated then try again")
                return
            resistors_dict['R13'] = R13*1000
            resistors_dict['R14'] = R14*1000
            resistors_dict['R8'] = R8*1000
            resistors_dict['R11'] = R11*1000
        
        display_resistors(resistors_dict, axis)
        return

            
          
    def help(self):
        """Launch the help window."""
        logging.info("Launching help window")
        settings.help_message(f"Please click on the link to a video tutorial for further instruction: {settings.SBT_HELP_LINK}", "Main")
        return
    
    def exit(self):
        """Exit the program
        Returns:
            KeyboardInterupt: this will colse the main window upon close of this window
        """
        self.close()
        logging.info("exited by user")
        return KeyboardInterrupt
    
    
def start_SBT_window():
    app = QtWidgets.QApplication(sys.argv)
    window = SBT_Window()  # noqa: F841
    app.exec_()
    