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

def load_WFS_named(input_dir,epsg_code):
    '''
    Load WFS genrated files
    Load in specific for case study with pre seprated named fires. Will need to modify directory structor of this for large scale unnamed runs 
    '''
    wfs_input_dir = Path(input_dir)/'WGC-G4-500-510'
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

    combined_gdf['geometry'] = combined_gdf['geometry'].make_valid()
    combined_gdf["area"] = combined_gdf.geometry.area
    # # filter so only the largest of the dat
    return combined_gdf

def load_wfs_nonames(input_dir,epsg_code):
    wfs_input_dir = input_dir
    print(wfs_input_dir)
    # dirs = []
    # for d in os.listdir(wfs_input_dir):
    #     if os.path.isdir(os.path.join(wfs_input_dir, d)):
    #         dirs.append(os.path.join(wfs_input_dir, d))
    dirs = [
    os.path.join(wfs_input_dir, d)
    for d in os.listdir(wfs_input_dir)
    if os.path.isdir(os.path.join(wfs_input_dir, d))
    ]
    final_dir = Path(dirs[-1])
    print(final_dir)
    files = []
    glob_func = final_dir.rglob 
    files.extend(glob_func(f'*_poly_perims.shp'))
    gdf = gpd.read_file(files[-1], engine="pyogrio").to_crs(epsg_code)
    gdf['geometry'] = gdf['geometry'].make_valid()

    return gdf

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
    gdfs = []
    for file in files:
        gdf = gpd.read_file(file, engine="pyogrio").to_crs(epsg_code)
        gdfs.append(gdf)
    if len(gdfs) > 1:
        combined_gdf = gpd.GeoDataFrame(
            pd.concat(gdfs, ignore_index=True),
            crs=epsg_code)
    else:
        combined_gdf = gdfs[0]
    combined_gdf['geometry'] = combined_gdf['geometry'].make_valid()
    combined_gdf["area"] = combined_gdf.geometry.area
    return combined_gdf


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

def relative_distance(geom1, geom2):
    """
    Calculate the relative percent difference 
    """
    a1 = geom1.area
    a2 = geom2.area

    # Avoid division by zero
    if a1 + a2 == 0:
        return 0.0
    
    num = abs(a1 - a2) 
    denom = (a1 + a2)/2
    p = num/denom
    return p * 100 


def compare_perimeters(wfs_df, nbac_df, nfdb_df):
    target_fires = wfs_df["name"].unique()
    result_gdfs = []
    for fire_name in target_fires:
        print(fire_name)
        for i, row_wfs in wfs_df[wfs_df["name"] == fire_name].iterrows():
            wfs_year = float(str(row_wfs['update_dt']).split("-")[0])
            for j, row_nbac in nbac_df.iterrows():
                if (row_wfs.geometry.intersects(row_nbac.geometry) and row_nbac["YEAR"] == wfs_year):
                    dice_value = dice_coefficient(row_wfs.geometry, row_nbac.geometry)
                    result_df = pd.DataFrame({
                    "NBAC_nfireid": row_nbac["NFIREID"],
                    "WFS_sandboxid": row_wfs["name"],
                    "event": row_wfs["event_id"],
                    "area": row_wfs.geometry.area,
                    "dice_coefficient": [dice_value]
                    })
                    result_gdfs.append(result_df)
            for k, row_nfdb in nfdb_df.iterrows():
                if (row_wfs.geometry.intersects(row_nfdb.geometry) and row_nfdb["YEAR"] == wfs_year):
                    dice_value = dice_coefficient(row_wfs.geometry, row_nfdb.geometry)
                    result_df = pd.DataFrame({
                    "NFDB_fireid": row_nfdb["FIRE_ID"],
                    "WFS_sandboxid": row_wfs["name"],
                    "event": row_wfs["event_id"],
                    "area": row_wfs.geometry.area,
                    "dice_coefficient": [dice_value]
                    })
                    result_gdfs.append(result_df)
    for i, row_nbac in nbac_df.iterrows():
        for j,row_nfdb in nfdb_df.iterrows():
            if (row_nbac.geometry.intersects(row_nfdb.geometry) and row_nbac["YEAR"] == row_nfdb["YEAR"]):
                dice_value = dice_coefficient(row_nbac.geometry, row_nfdb.geometry)
                result_df = pd.DataFrame({
                    "NBAC_nfireid": row_nbac["NFIREID"],
                    "NFDB_fireid": row_nfdb["FIRE_ID"],
                    "dice_coefficient": [dice_value]
                    })
                result_gdfs.append(result_df)

    combined_gdf = pd.concat(result_gdfs, ignore_index=True)
    
    return combined_gdf

def compare_perimeters_nonames(wfs_df, nbac_df, nfdb_df):
    result_gdfs = []
    for i, row_wfs in wfs_df.iterrows():
        print("working on:")
        print(row_wfs["event_id"])
        for j, row_nbac in nbac_df.iterrows():
            if row_wfs.geometry.intersects(row_nbac.geometry):
                dice_value = dice_coefficient(row_wfs.geometry, row_nbac.geometry)
                RPD_value = relative_distance(row_wfs.geometry, row_nbac.geometry)
                result_df = pd.DataFrame({
                "NBAC_nfireid": row_nbac["NFIREID"],
                "NBAC_area": row_nbac.geometry.area,
                "WFS event": row_wfs["event_id"],
                "T2_area": row_wfs.geometry.area,
                "dice_coefficient": [dice_value],
                "Relative Percent Difference": [RPD_value]
                })
                result_gdfs.append(result_df)
        for k, row_nfdb in nfdb_df.iterrows():
            if row_wfs.geometry.intersects(row_nfdb.geometry):
                dice_value = dice_coefficient(row_wfs.geometry, row_nfdb.geometry)
                RPD_value = relative_distance(row_wfs.geometry, row_nfdb.geometry)
                result_df = pd.DataFrame({
                "NFDB_fireid": row_nfdb["FIRE_ID"],
                "NFDB_area": row_nfdb.geometry.area,
                "WFS event": row_wfs["event_id"],
                "T2_area": row_wfs.geometry.area,
                "dice_coefficient": [dice_value],
                "Relative Percent Difference": [RPD_value]
                })
                result_gdfs.append(result_df)
               
    for i, row_nbac in nbac_df.iterrows():
        for j,row_nfdb in nfdb_df.iterrows():
            if row_nbac.geometry.intersects(row_nfdb.geometry):
                dice_value = dice_coefficient(row_nbac.geometry, row_nfdb.geometry)
                RPD_value = relative_distance(row_nbac.geometry, row_nfdb.geometry)
                result_df = pd.DataFrame({
                    "NBAC_nfireid": row_nbac["NFIREID"],
                    "NBAC_area": row_nbac.geometry.area,
                    "NFDB_fireid": row_nfdb["FIRE_ID"],
                    "NFDB_area": row_nfdb.geometry.area,
                    "dice_coefficient": [dice_value],
                    "Relative Percent Difference": [RPD_value]
                    })
                result_gdfs.append(result_df)

    combined_gdf = pd.concat(result_gdfs, ignore_index=True)
    
    return combined_gdf



def dice_area_plot(
    df: pd.DataFrame,
    area_col: str = "area",
    dice_col: str = "dice_coefficient",
    n_bins: int = 10
):
    # Work on a copy to avoid modifying caller's dataframe
    data = df.copy()

    # Create area bins
    # data["area_bin"] = pd.cut(
    #     data[area_col],
    #     bins=n_bins,
    #     precision=0
    # )
    data["area_bin"] = pd.qcut(data[area_col],
                               q=n_bins,
                               precision=0)
    

    grouped = data.groupby("area_bin")
    print(grouped.groups)
    bins = data["area_bin"].cat.categories
    print(bins)
    grouped_data = []
    for bin in bins:
        values = grouped.get_group(bin)["dice_coefficient"].values
        grouped_data.append(values)

    # Create box-and-whisker plot
    plt.figure(figsize=(10, 6))
    plt.boxplot(grouped_data, labels=[str(b) for b in bins], showfliers=True)

    plt.xlabel("Area bins")
    plt.ylabel("Dice coefficient")
    plt.title("Dice Coefficient Distribution by Area Bins")

    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.show()

def dice_bar_plot(dataframe, xaxis, yaxis):
    
    dataframe.plot(
        x=xaxis,
        y=yaxis,
        kind="bar",
        legend=False,
        figsize=(8, 5)
    )

    plt.xlabel(xaxis)
    plt.ylabel(yaxis)
    plt.tight_layout()
    plt.show()


    # combined_gdf = gpd.GeoDataFrame(pd.concat(gdfs, ignore_index=True), crs=gdfs[0].crs)
    # print(combined_gdf.head())


def named_sandbox_compare():
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
    WFS_df_all = load_WFS_named(config.get("PATH_TO_INPUT_DIR"),config.get("EPSG_NUMBER"))
    #Improt NBAC
    NBAC_df_all = load_NBAC(config.get("PATH_TO_INPUT_DIR"),config.get("EPSG_NUMBER"))
    print('NBAC loaded')
    # #Import NFDB
    NFDB_df_all = load_NFDB(config.get("PATH_TO_INPUT_DIR"),config.get("EPSG_NUMBER"))
    print('NFDB loaded')
    #Filter down to relavent fires 
    nbac_df_filtered, nfdb_df_filtered = subset_NFBD_NBAC(WFS_df_all,NBAC_df_all,NFDB_df_all)
    # nbac_df_filtered = subset_NFBD_NBAC(WFS_df_all,NBAC_df_all,None)
    #Apply custome Dice Score 
    results_df = compare_perimeters(WFS_df_all, nbac_df_filtered, nfdb_df_filtered)
    # results_df = compare_perimeters(WFS_df_all, nbac_df_filtered, None)
    # results_df.to_csv('dice_out_03_27.csv')
    filtered_df = results_df.loc[results_df.groupby("WFS_sandboxid")["area"].idxmax()]
    print(filtered_df)
    return filtered_df

def subset_year_compare(agency_id,year):
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
    print(config)

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
    print(config.get("EPSG_NUMBER"))

    print(config.get("PATH_TO_INPUT_DIR"))
    #Import in T2 data
    WFS_df_all = load_wfs_nonames(config.get("PATH_TO_INPUT_DIR"),config.get("EPSG_NUMBER"))
    print("wfs_loaded")
    #Improt NBAC
    NBAC_df_all = load_NBAC(config.get("PATH_TO_INPUT_DIR"),config.get("EPSG_NUMBER"))
    print('NBAC loaded')
    #Import NFDB
    NFDB_df_all = load_NFDB(config.get("PATH_TO_INPUT_DIR"),config.get("EPSG_NUMBER"))
    print('NFDB loaded')
    # print(NFDB_df_all.info())
    # Filter down by year and province
    nbac_df_filtered = NBAC_df_all[(NBAC_df_all['YEAR'] == float(year)) & (NBAC_df_all['ADMIN_AREA'] == agency_id)]
    nfdb_df_filtered = NFDB_df_all[(NFDB_df_all['YEAR'] == year) & (NFDB_df_all['SRC_AGENCY'] == agency_id)]
    # print(nfdb_df_filtered)
    results_df = compare_perimeters_nonames(WFS_df_all, nbac_df_filtered, nfdb_df_filtered)
    results_df.to_csv('April10.csv')
    return results_df

def main():
    results_df = subset_year_compare(agency_id = 'SK', year = 2023)
    # dice_bar_plot(results_df, 'WFS_sandboxid', 'dice_coefficient')
    # dice_area_plot(results_df)




# =============================================================================
# Application entrypoint
# =============================================================================
if __name__ == "__main__":
    main()