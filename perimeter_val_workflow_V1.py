# ============================================================================
# Imports
# ============================================================================
from pathlib import Path
from sys import argv, path
import logging
from yaml import safe_load, YAMLError
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import os
import pyogrio

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

def load_WFS(input_dir,epsg_code):
    '''
    Load WFS genrated files
    Load in specific for case study with pre seprated named fires. Will need to modify directory structor of this for large scale unnamed runs 
    '''
    wfs_input_dir = Path(input_dir)/'WGC-G4-500-510'
    
    # dirs = []
    # for path, subdirs, files in os.walk(wfs_input_dir):
    #     for s in subdirs:
    #         dirs.append(os.path.join(path, s))

    # final_dir = Path(dirs[-1])

    # files = []
    # glob_func = wfs_input_dir.rglob 
    # files.extend(glob_func(f'*_poly_perims.shp'))
    # print(files)
     
    dirs = [
    os.path.join(wfs_input_dir, d)
    for d in os.listdir(wfs_input_dir)
    if os.path.isdir(os.path.join(wfs_input_dir, d))
    ]
    gdfs = []
    for dir in dirs:
        print(dir)
        sub_dirs = []
        for path, subdirs, files in os.walk(dir):
            for s in subdirs:
                sub_dirs.append(os.path.join(path, s))
        final_dir = Path(sub_dirs[-1])
        print(final_dir)
        files = []
        glob_func = final_dir.rglob 
        files.extend(glob_func(f'*_poly_perims.shp'))
        subdir_name = Path(dir).name
        gdf = gpd.read_file(files[-1], engine="pyogrio")
        gdf["name"] = subdir_name
        gdfs.append(gdf)


    combined_gdf = gpd.GeoDataFrame(
        pd.concat(gdfs, ignore_index=True),
        crs=epsg_code)

    # combined_gdf = gpd.read_file(files[-1], engine="pyogrio").to_crs(epsg_code)
    # subdir_name = str(files[-1]).split('\\')[4]
    # combined_gdf["name"] = subdir_name
    combined_gdf['geometry'] = combined_gdf['geometry'].make_valid()
    combined_gdf["area"] = combined_gdf.geometry.area
    # # filter so only the largest of the dat
    return combined_gdf

def load_NFDB(input_dir,epsg_code):
    '''
    Load NFDB genrated files
    '''
    nfdb_input_dir = Path(input_dir)/'NFDB'
    files = []
    glob_func = nfdb_input_dir.rglob 
    files.extend(glob_func(f'*.shp'))
    gdf = gpd.read_file(files[0], engine="pyogrio").to_crs(epsg_code)
    gdf['geometry'] = gdf['geometry'].make_valid()
    return gdf

def load_NBAC(input_dir,epsg_code):
    '''
    Load NFDB genrated files
    '''
    nfdb_input_dir = Path(input_dir)/'NBAC'
    files = []
    glob_func = nfdb_input_dir.rglob 
    files.extend(glob_func(f'*.shp'))
    gdf = gpd.read_file(files[0], engine="pyogrio").to_crs(epsg_code)
    gdf['geometry'] = gdf['geometry'].make_valid()
    return gdf

def subset_NFBD_NBAC(wfs_df, nbac_df, nfdb_df):
    target_fires = wfs_df["name"].unique()
    years = []
    for fire in target_fires:
        # final_row = wfs_df[wfs_df["name"] == fire].tail(1)
        final_row = wfs_df[wfs_df["name"] == fire].iloc[-1]
        year = str(final_row['update_dt']).split("-")[0]
        years.append(float(year))
    print('years')
    print(years)
    wfs_df['geometry'] = wfs_df['geometry'].make_valid()
    geom_union = wfs_df.union_all()
    nbac_df_filtered = nbac_df[nbac_df["YEAR"].isin(years)][nbac_df[nbac_df["YEAR"].isin(years)].intersects(geom_union)]   
    nfdb_df_filtered = nfdb_df[nfdb_df["YEAR"].isin(years)][nfdb_df[nfdb_df["YEAR"].isin(years)].intersects(geom_union)]   

    return nbac_df_filtered, nfdb_df_filtered
    # return nbac_df_filtered 
    

def dice_coefficient(geom1, geom2):
    """
    Computes the Dice coefficient between two Shapely geometries.
    """
    # Area of intersection
    inter = geom1.intersection(geom2).area

    # Areas of individual geometries
    a1 = geom1.area
    a2 = geom2.area

    # Avoid division by zero
    if a1 + a2 == 0:
        return 0.0
    
    return (2 * inter) / (a1 + a2)

def compare_perimeters(wfs_df, nbac_df, nfdb_df, epsg_code):
    target_fires = wfs_df["name"].unique()
    result_gdfs = []
    for fire_name in target_fires:
        print(fire_name)
        for i, row_wfs in wfs_df[wfs_df["name"] == fire_name].iterrows():
            for j, row_nbac in nbac_df.iterrows():
                if row_wfs.geometry.intersects(row_nbac.geometry):
                    dice_value = dice_coefficient(row_wfs.geometry, row_nbac.geometry)
                    result_df = pd.DataFrame({
                    "nfireidname": row_nbac["NFIREID"],
                    "fire name": row_wfs["name"],
                    "event": row_wfs["event_id"],
                    "dice_coefficient": [dice_value]
                    })
                    print(row_wfs['name'])
                    print(row_wfs)
                    result_gdfs.append(result_df)
            for k, row_nfdb in nfdb_df.iterrows():
                if row_wfs.geometry.intersects(row_nfdb.geometry):
                    dice_value = dice_coefficient(row_wfs.geometry, row_nfdb.geometry)
                    result_df = pd.DataFrame({
                    "agency label": row_nfdb["FIRE_ID"],
                    "fire name": row_wfs["name"],
                    "event": row_wfs["event_id"],
                    "dice_coefficient": [dice_value]
                    })
                    result_gdfs.append(result_df)

    combined_gdf = pd.concat(result_gdfs, ignore_index=True)
    
    return combined_gdf







    



    # combined_gdf = gpd.GeoDataFrame(pd.concat(gdfs, ignore_index=True), crs=gdfs[0].crs)
    # print(combined_gdf.head())



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
    WFS_df_all = load_WFS(config.get("PATH_TO_INPUT_DIR"),config.get("EPSG_NUMBER"))
    print(WFS_df_all)

    #Improt NBAC
    NBAC_df_all = load_NBAC(config.get("PATH_TO_INPUT_DIR"),config.get("EPSG_NUMBER"))
    # #Import NFDB
    NFDB_df_all = load_NFDB(config.get("PATH_TO_INPUT_DIR"),config.get("EPSG_NUMBER"))
    #Filter down to relavent fires 
    nbac_df_filtered, nfdb_df_filtered = subset_NFBD_NBAC(WFS_df_all,NBAC_df_all,NFDB_df_all)
    # nbac_df_filtered = subset_NFBD_NBAC(WFS_df_all,NBAC_df_all,None)
    print(nfdb_df_filtered.tail())
    print(nbac_df_filtered.tail())
    #Apply custome Dice Score 
    results_df = compare_perimeters(WFS_df_all, nbac_df_filtered, nfdb_df_filtered, None)
    print(results_df)
    results_df.to_csv('dice_out.csv')
    


# =============================================================================
# Application entrypoint
# =============================================================================
if __name__ == "__main__":
    main()