import sys
import logging
import os
import pandas 
from network import router_methods
from analytics import numerical_methods
from system import settings
from network import api_calls
from PyQt5 import QtWidgets, uic, QtGui
from PyQt5.QtCore import Qt




def read_data(serial_no, data):
    bias = 0
    sf = 0
    filtered_data = data[data["Serial Number"] == serial_no].head()
    row = filtered_data.tail(1)
    try:
        row_num = int(row.index[0])
    except Exception as e:
        settings.error_message(f"no data was found for serial number: {serial_no}, please confirm work order and serial number details are correct and the unit has been calibrated then try again")
        logging.info(f"Official error message: {e}")
        return "fail", "fail", "fail", "fail"
    bias = float(data.iloc[row_num,1])
    logging.info(f"Found bias resistor value: {bias}")
    sf = float(data.iloc[row_num,2])
    logging.info(f"Found SF resistor value: {sf}")
    bias1, bias2 = numerical_methods.calculate_resistors_in_parallel(bias*1000)
    sf1, sf2 = numerical_methods.calculate_resistors_in_parallel(sf*1000)
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
    text = ""
    i = 0
    j = 0
    for key, value in resistor_dict.items():
        j +=1
        resistor = f"On {key} install a {value} resistor"
        ending = "\n"
        if j == len(resistor_dict):
            ending = ""
        elif i < 3:
            ending = "      "
            i+=1
        else:
            i=0
        text = text + resistor + ending
    #display popup
    logging.info(f"Text displayed to the user: {text}")
    logging.info(f"Pic displayed to the user: {pic}")
    popup = ImagePopup(image_path, text)
    popup.exec_()
    return

class ImagePopup(QtWidgets.QDialog):
    def __init__(self, image_path, text, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Install the following resistors:")
        self.setFixedWidth(1800)
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
        layout.addWidget(image_label, alignment=Qt.AlignCenter)

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
        logging.info(settings.WINDOWS_BASE)
        ui_file = os.path.join(settings.WINDOWS_BASE, "SBT_window.ui")
        # load the ui file
        uic.loadUi(ui_file, self)

        # PUSH BUTTONS
        ############################################################################
        self.sn_barcode_sn_pb = self.findChild(QtWidgets.QPushButton, "sn_barcode_pb")
        self.sn_barcode_sn_pb.clicked.connect(self.barcode_sn)
        
        self.update_pb = self.findChild(QtWidgets.QPushButton, "update_pb")
        self.update_pb.clicked.connect(self.update_sn)

        self.help_pb = self.findChild(QtWidgets.QPushButton, "help_pb")
        self.help_pb.clicked.connect(self.help)

        self.exit_pb = self.findChild(QtWidgets.QPushButton, "exit_pb")
        self.exit_pb.clicked.connect(self.exit)
        ############################################################################

        #COMBO BOXES:
        ############################################################################
        self.status_cobo = self.findChild(QtWidgets.QComboBox, "status_cobo")
        ############################################################################
        
        # LINE EDITS:
        ############################################################################
        self.serial_number_le = self.findChild(QtWidgets.QLineEdit, "serial_number_le")
        ############################################################################

        self.status_cobo.setCurrentText(settings.last_pushed)
        self.show()



    def barcode_sn(self):
        """Allows the user to scan their keycard to log in if they have logged in once before
        """
        logging.info("The serial number barcode button has been pressed")
        dialog = BarcodeEntryPopup(self)
        if dialog.exec_():
            response = dialog.barcode_value.text()
            if response != "":  
                matrix = response.split(",")
                desc = matrix[2]
                logging.info(f"The user scanned the barcode containing: {response} as the user info")
                logging.info(f"The scanned response resulted in the following discription: {desc}")
                self.serial_number_le.setText(desc)
        return
    
  

    def update_sn(self):
        logging.info("update_sn button pushed")
        sn = self.serial_number_le.text()
        if self.status_cobo.text() != "":
            status = settings.analog_method_order[self.status_cobo.text()]
        else:
            status = settings.analog_method_order[settings.last_pushed]
        router_methods.update_sn_status(sn, status)
        settings.message(f"the status of {sn} has sucessfull been updated to ready for {status}")
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
    