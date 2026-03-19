# ============================================================================
# Imports
# ============================================================================
from pathlib import Path
from sys import argv, path
import logging
from yaml import safe_load, YAMLError


# ============================================================================
__author__ = "Julia Harvie, Morgan Crowley, Alan Cantin, Jacqueline Oliver"
__copyright__ = "Julia Harvie, Morgan Crowley, Alan Cantin, Jacqueline Oliver"
__credits__ = ["Julia Harvie, Morgan Crowley, Alan Cantin, Jacqueline Oliver"]
__license__ = ""
__version__ = "0.1"
__maintainer__ = "Julia Harvie"
__email__ = """
            julia.harvie@nrcan-rncan.gc.ca,
            morgan.crowley@nrcan-rncan.gc.ca,
            alan.cantin@nrcan-rncan.gc.ca
            """
__status__ = ""


# ============================================================================
# Application description
# ============================================================================
"""


"""

def config_logging(log_file_path=None,
                   log_level="INFO",
                   log_to_console=True):
    """
    Configures the logging settings for the application.

    Args:
        log_file_path (str or Path, optional): Path to the log file. If None,
          logs will be output to the console only.
        log_level (str, optional): Logging level. Defaults to "INFO".

    Raises:
        ValueError: If the provided log level is invalid.
    """
    # Validate the log level
    log_level = log_level.upper()
    if log_level not in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
        raise ValueError(f"Invalid log level: {log_level}")

    # Create a logging configuration
    log_handlers = []

    if log_file_path:
        log_file_path = Path(log_file_path)

        # Ensure the directory for the log file exists
        log_file_path.parent.mkdir(parents=True, exist_ok=True)

        # Add a FileHandler to write logs to the file
        file_handler = logging.FileHandler(log_file_path)
        file_handler.setFormatter(
            logging.Formatter('%(asctime)s %(levelname)s:%(message)s')
        )
        log_handlers.append(file_handler)

    if log_to_console:
        # Add a StreamHandler to write logs to the console
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(
            logging.Formatter('%(asctime)s %(levelname)s:%(message)s')
        )
        log_handlers.append(console_handler)

    # Configure the root logger
    logging.basicConfig(
        level=getattr(logging, log_level),
        handlers=log_handlers
    )

    logging.info("Logging has been configured.")

def find_project_root(marker_name="config"):
    """
    Search for a marker file or directory in the directory tree and return the
    path of the first occurrence. The search starts from the directory of the
    current file and moves up the directory tree until the root directory is
    reached.

    args:
        marker_name (str): Name of the marker file or directory to search for

    returns:
        Path: Path of the first occurrence of the marker file or directory

    raises:
        FileNotFoundError: If the marker file or directory is not found in the
            directory tree
    """
    current_dir = Path(__file__).resolve().parent
    root_dir = Path(current_dir.root)

    # Move up directory tree until marker file or directory is found
    # Stop if root directory is reached
    while current_dir != root_dir:
        if (current_dir / marker_name).exists():
            return current_dir
        current_dir = current_dir.parent

    # Final check in case marker file or directory is in root directory
    if (current_dir / marker_name).exists():
        return current_dir

    raise FileNotFoundError(f"Marker '{marker_name}' not found in directory "
                            "tree"
                            )

def load_config(path):
    """
    Basic function to safely load a config file.

    Args:
        path (str): Path to config file.

    Raises:
        ValueError: If config file is empty.
        FileNotFoundError: If the file does not exist.
        yaml.YAMLError: If there is an error parsing the YAML file.

    Returns:
        dict: Safe load of config file content.
    """
    config_path = Path(path)
    # sib_test_fun()
    if not config_path.exists():
        raise FileNotFoundError(f"Config file '{path}' does not exist.")

    with config_path.open("r", encoding="utf-8") as file:
        try:
            content = file.read().strip()
            if not content:
                raise ValueError("The config file is empty.")

            return safe_load(content)

        except YAMLError as yaml_error:
            raise YAMLError(
                f"Error parsing YAML file '{path}': {yaml_error}"
            ) from yaml_error

def load_WFS(input_dir):
    '''
    Load WFS geenrated files
    '''
    wfs_input_dir = Path(input_dir)/'WGC-G4-500-510'
    
    
    files = []
    glob_func = wfs_input_dir.rglob 
    files.extend(glob_func(f'*.shp'))
    data_frames = []
    for file_path in files:
        print(file_path)
            # curr_df = self._load_file(file_path)
            # if curr_df is not None:
            #     data_frames.append(curr_df)


def main():

    # Load config
    # ------------------------------------------------------------------------
    # Initialize config_path variable
    # Determine if the provided argument is a valid YAML file (.yml or .yaml)
    if len(argv) > 1 and Path(argv[1]).suffix in ['.yml', '.yaml']:
        config_path = Path(argv[1])
    # Use the default path if the second argument isn't a valid config file
    else:
        proj_dir = find_project_root("config")
        config_path = proj_dir / "config" / "config_stub.yml" 
    config = load_config(config_path)

    # Initialization and Data Loading
    # ------------------------------------------------------------------------
    # Get core config values
    EPSG_NUMBER = config.get("EPSG_NUMBER")
    if not EPSG_NUMBER:
        raise ValueError("EPSG_NUMBER is required in configuration")
    if not isinstance(EPSG_NUMBER, int) or EPSG_NUMBER <= 0:
        raise ValueError("EPSG_NUMBER must be a positive integer")

    # Logging config - optional - if not set, will print to console
    config_logging(config.get("PATH_TO_LOG_OUTPUT"),
                   config.get("LOG_LEVEL"),
                   config.get("LOG_TO_CONSOLE"))
    config


    #Import in T2 data
    WFS_df = load_WFS(config.get("PATH_TO_INPUT_DIR"))
    #Improt NBAC
    #Import NFDB
    #Apply case study filte (only fires that overlap)
    #Apply custome Dice Score 
    None


# =============================================================================
# Application entrypoint
# =============================================================================
if __name__ == "__main__":
    main()