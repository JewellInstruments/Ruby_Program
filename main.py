"""
Author: Cam Brochu
Date: 6/11/2025
About: This app pull of the correct RUBY assembly power point
"""

#imports:
import window.main_window as main_window
import window.login_window as login_window
import system.settings  as settings
import system.log_config as log_config
import logging
import ctypes

def main():
    ctypes.windll.user32.ShowWindow( ctypes.windll.kernel32.GetConsoleWindow(), 6 )
    try:
        logging.info("starting login window")
        login_window.start_login_window()
        if settings.LOGGED_IN is True:
            logging.info("starting main window")
            main_window.start_main_window()
    except KeyboardInterrupt:
        logging.info("User aborted app")
        print("User aborted app")
    except Exception as e:
        logging.info(f"main.py Error: {e}")
        print(f"Error: {e}")
    finally:
        logging.info("closing program")
        print("closing program")
    return

if __name__ == "__main__":
    log_config.configure_logging(settings.log_file_path)
    main()
