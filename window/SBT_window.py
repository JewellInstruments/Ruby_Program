import sys
import logging
import os
import keyring
import system.settings as settings
import system.api_calls as api_calls
from PyQt5 import QtWidgets, uic
import pandas

def read_data(data):
    bias1 = 0
    bias2 = 0
    sf1 = 0
    sf2 = 0
    return bias1, bias2, sf1, sf2

def display_resistors():
    return

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
        self.sn_barcode_pb = self.findChild(QtWidgets.QPushButton, "sn_barcode_pb")
        self.sn_barcode_pb.clicked.connect(self.barcode)
        
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
        ############################################################################
        self.show()



    def barcode(self):
        """Allows the user to scan their keycard to log in if they have logged in once before
        """
        dialog = BarcodeEntryPopup(self)
        if dialog.exec_():
            response = dialog.barcode_value.text()
            matrix = response.split(",")
            desc = matrix[1]
            #seperate the matrix data by comma
            logging.info(f"The user scanned the barcode containing: {response} as the user info")
            logging.info(f"The scanned response resulted in the following discription: {desc}")
        self.serial_number_le.setText(desc)
        return
    

    def start(self):
        """_summary_
        This function checks the provided login information and if true passes the entered info to the next window
        """
        logging.info("SBT start button pushed")
        desc = settings.ruby_conversion_chart[settings.work_order_part_no.strip()]
        description = desc.split("-")
        print(f"description: {description}")
        if description == ['']:
            settings.error_message("You have not selected an option")
            return 
        unit_range = str(description[4])
        if str(description[0]) == 'JMHA':
            unit_range = f"{unit_range}g"
        file_name = f"RUBY {str(desc[3])} {unit_range}.xlsx"
        try:
            file = os.path.join(settings.EXCEL_BASE, file_name)
        except Exception:
            print(file_name)
            settings.error_message("Error: Calibration data file cannot be found!")
            return
        
        axis = description[1][0:]
        print(f"axis #: {axis}")
        x_data = pandas.read_excel(file, sheet_name="X axis")
        y_data = pandas.read_excel(file, sheet_name="Y axis")
        z_data = pandas.read_excel(file, sheet_name="Z axis")
        R13, R14, R8, R11 = read_data(x_data)
        R20, R21, R15, R18 = read_data(y_data)
        R27, R28, R8, R11 = read_data(z_data)

        

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
    