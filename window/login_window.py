import sys
import logging
import os
import keyring
from system import settings
from network import api_calls
from PyQt5 import QtWidgets, uic

def get_info_from_barcode(self) -> str:
    dialog = BarcodeEntryPopup(self)
    if dialog.exec_():
        response = dialog.barcode_value.text()
        logging.info(f"The user scanned the barcode containing: {response} as the user info")
    return response

def store_login_info(ID, username, password):
    saved_username_for_current_id = keyring.get_password(settings.username_table, ID)
    saved_username_for_current_id = saved_username_for_current_id
    if saved_username_for_current_id is not None:
        saved_username_for_current_id = saved_username_for_current_id.strip("@jewellinstruments.com")
    saved_password_for_current_username = keyring.get_password(settings.password_table, username)
    try:
        if (saved_username_for_current_id != username) and (saved_username_for_current_id is not None):
            keyring.delete_password(settings.username_table, ID)
            saved_username_for_current_id = None
        if (saved_password_for_current_username != password) and (saved_password_for_current_username is not None):
            keyring.delete_password(settings.password_table, username)
            saved_password_for_current_username = None
        if (saved_username_for_current_id is None):
            keyring.set_password(settings.username_table, ID, username)
            logging.info(f"updating the username for ID: {ID} has been saved")
        if (saved_password_for_current_username is None):
            keyring.set_password(settings.password_table, username, password)
            logging.info(f"updating the password for username: {username} has been saved")
    except Exception as e:
        settings.error_message(f"an unknown error: {e} has occured")
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

class Login_Window(QtWidgets.QMainWindow):
    def __init__(self):
        super(Login_Window, self).__init__()
        # get the path to the ui file
        print(settings.WINDOWS_BASE)
        logging.info(settings.WINDOWS_BASE)
        ui_file = os.path.join(settings.WINDOWS_BASE, "login_window.ui")
        # load the ui file
        uic.loadUi(ui_file, self)

        # PUSH BUTTONS
        ############################################################################
        self.login_pb = self.findChild(QtWidgets.QPushButton, "login_pb")
        self.login_pb.clicked.connect(self.login)

        self.user_barcode_pb = self.findChild(QtWidgets.QPushButton, "user_barcode_pb")
        self.user_barcode_pb.clicked.connect(self.user_barcode)

        self.work_order_barcode_pb = self.findChild(QtWidgets.QPushButton, "work_order_barcode_pb")
        self.work_order_barcode_pb.clicked.connect(self.work_order_barcode)

        self.help_pb = self.findChild(QtWidgets.QPushButton, "help_pb")
        self.help_pb.clicked.connect(self.help)

        self.exit_pb = self.findChild(QtWidgets.QPushButton, "exit_pb")
        self.exit_pb.clicked.connect(self.exit)
        ############################################################################
        
        # LINE EDITS:
        ############################################################################
        self.work_order_le = self.findChild(QtWidgets.QLineEdit, "work_order_le")
        self.user_le = self.findChild(QtWidgets.QLineEdit, "username_le")
        self.password_le = self.findChild(QtWidgets.QLineEdit, "password_le")
        self.ID_number_le = self.findChild(QtWidgets.QLineEdit, "ID_number_le")
        ############################################################################
        self.show()

    def login(self):
        """_summary_
        This function checks the provided login information and if true passes the entered info to the next window
        """
        logging.info("login button pushed")
        user_name = self.user_le.text()
        if user_name != '':
            if "@" not in user_name:
                user_name += "@jewellinstruments.com"
        API_responce = api_calls.APIHandler(login_email=user_name, login_pass=str(self.password_le.text())).login()
        if API_responce is False:
            settings.Login_fail_count += 1
            logging.info(f"{user_name} failed to log in")
            if settings.Login_fail_count >= 3:
                settings.error_message("Incorrect Login Information, Maximum login attempts reached")
                self.close()
                return 
            else:
                settings.error_message("Incorrect Login Information, please try again")  
        elif API_responce is True:
            require_work_order = False
            if self.work_order_le.text() != '':
                found = False
                require_work_order = True
                try:
                    settings.work_order, sales_order, customer, settings.work_order_part_no, settings.qty = api_calls.get_work_order(self.work_order_le.text())
                    found = True
                    logging.info(f"workorder: {settings.work_order} found")
                except Exception as e:
                    logging.info(f"login_window.py Error: {e}")
                    settings.error_message("Failed to find work order")
            if require_work_order is True:
                if found is True:
                    settings.LOGGED_IN = True
            else:
                settings.LOGGED_IN = True
            if settings.LOGGED_IN is True:
                store_login_info(self.ID_number_le.text(), self.user_le.text(), self.password_le.text())
                self.close()
                logging.info(f"{user_name} sucessfully logged in")
                return 
            
        
    def user_barcode(self):
        """Allows the user to scan their keycard to log in if they have logged in once before
        """
        response = get_info_from_barcode(self) #at this point response should be a string of a 5 digit number that is the employee id
        self.ID_number_le.setText(response)
        try: 
            username = keyring.get_password(settings.username_table, response)
            password = keyring.get_password(settings.password_table, username)
            self.username_le.setText(username)
            self.password_le.setText(password)
        except KeyError:
            settings.error_message(f"user id: {response} from barcode not found, please enter login info manually and next time you can use the barcode function")
        except Exception as e:
            settings.error_message(f"an unknown error: {e} has occured") 
        return
    
    def work_order_barcode(self):
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
    
    def help(self):
        """Launch the help window."""
        logging.info("Launching help window")
        settings.help_message(f"Please click on the link to a video tutorial for further instruction: {settings.LOGIN_HELP_LINK}", "Main")
        return
    
    def exit(self):
        """Exit the program
        Returns:
            KeyboardInterupt: this will colse the main window upon close of this window
        """
        self.close()
        logging.info("exited by user")
        return KeyboardInterrupt
    
    
def start_login_window():
    app = QtWidgets.QApplication(sys.argv)
    window = Login_Window()  # noqa: F841
    app.exec_()
    