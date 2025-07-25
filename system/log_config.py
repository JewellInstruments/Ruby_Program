import logging
import os
import sys
#import datetime

from system import settings

def init_directory(filepath: str) -> None:
    """create a new folder if one does not already exist.
    Args:
        filepath (str): path to folder to create.
    """
    if not os.path.isdir(filepath):
        logging.info("Directory is not set up... setting up now...")
        os.makedirs(filepath, exist_ok=False)
    return


def configure_logging(log_file_path: str) -> None:
    """configure the logging.
    Args:
        log_file_path (str): filepath for where to create the log files.
    """
    print("Setting up logging...")
    init_directory(log_file_path)
    logging.basicConfig(filename=os.path.join(settings.log_file_path, "error.log"), level=settings.LOG_LEVEL, format=settings.log_format)
    logging.getLogger(__name__).addHandler(logging.StreamHandler(sys.stdout))
    return
