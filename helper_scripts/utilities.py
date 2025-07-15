"""Utility functions for Total War Warhammer 3 modding."""

import pandas as pd
import subprocess
import os
import shutil
import logging
from typing import List, Dict


FILEPATH_TO_VANILLA_DATA_TABLES = r"C:\SteamLibrary\steamapps\common\Total War WARHAMMER III\data\db.pack"

# TSV file structure constants
HEADER_ROW_INDEX = 0
VERSION_ROW_INDEX = 1
DATA_START_ROW = 2

def extract_tsv_data(table_name: str):
    """Extract the TSV data for a given table name from the vanilla data tables to a folder prepended with \"vanilla_\".
    
    Args:
        table_name (str): The name of the table to extract.
    """
    subprocess.run([
        "./rpfm_cli.exe",
        "--game",
        "warhammer_3",
        "pack",
        "extract",
        "--pack-path",
        FILEPATH_TO_VANILLA_DATA_TABLES,
        "--tables-as-tsv",
        "./schemas/schema_wh3.ron",
        "--file-path",
        f"db/{table_name}/data__;./vanilla_{table_name}"
    ])
    
    logging.info(f"TSV file \"{table_name}\" successfully extracted.")

def extract_modded_tsv_data(table_name: str, packfile_path: str, extract_path: str):
    """Extract the TSV data for a given table name from the modded data tables.
    
    Args:
        table_name (str): The name of the table to extract.
        packfile_path (str): The path to the packfile to extract from.
        extract_path (str): The path to extract the TSV data to.
    """
    subprocess.run([
        "./rpfm_cli.exe",
        "--game",
        "warhammer_3",
        "pack",
        "extract",
        "--pack-path",
        packfile_path,
        "--tables-as-tsv",
        "./schemas/schema_wh3.ron",
        "--folder-path",
        f"db/{table_name};{extract_path}"
    ])

    if not os.path.exists(extract_path):
        logging.warning(f"No TSV file(s) for \"{table_name}\" found in {extract_path} for the mod \"{packfile_path.split('/')[-1]}\".")
    else:
        logging.info(f"TSV file(s) for \"{table_name}\" successfully extracted to {extract_path} for the mod \"{packfile_path.split('/')[-1]}\".")

def load_tsv_data(file_path: str):
    """Load and parse TSV file into structured data.
    
    Args:
        file_path (str): Path to TSV file to load.
        
    Returns:
        A tuple of a list of row dictionaries with header keys, the headers, and version information.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    headers = lines[HEADER_ROW_INDEX].strip().split("\t")
    version_info = lines[VERSION_ROW_INDEX].strip()
    
    data = []
    for line in lines[DATA_START_ROW:]:
        if not line.strip():
            # Skip empty lines
            continue
        values = line.strip().split("\t")
        data.append(dict(zip(headers, values)))
    
    return data, headers, version_info

def load_multiple_tsv_data(folder_path: str):
    """Load all TSV files in a folder and parse them all into a single list of structured data.
    
    Args:
        folder_path (str): Path to the folder containing the TSV files.
        
    Returns:
        A tuple of a list of row dictionaries with header keys, the headers, and version information of which the latter belongs to the first TSV file found.
    """
    merged_data_set = set()
    headers = None
    version_info = None
    for file_name in os.listdir(folder_path):
        if file_name.endswith(".tsv"):
            temp_data, temp_headers, temp_version_info = load_tsv_data(os.path.join(folder_path, file_name))
            # Convert each row dict to a tuple of items for set storage.
            for row in temp_data:
                merged_data_set.add(tuple(row.items()))
            if headers is None:
                headers = temp_headers
            if version_info is None:
                version_info = temp_version_info

    # Convert back to list of dictionaries.
    merged_data = [dict(row_tuple) for row_tuple in merged_data_set]
    logging.info(f"Loaded a total of {len(merged_data)} unique rows for {folder_path}.")
    return merged_data, headers, version_info

def read_and_clean_tsv(tsv_file_path: str, table_type: str, allowed_patterns: List[str] = None):
    """Load and clean TSV file based on the table type.
    
    Args:
        tsv_file_path (str): Path to the TSV file.
        table_type (str): Type of the table to determine cleaning rules.
        allowed_patterns (List[str], optional): Patterns to allow in specific columns.
        
    Returns:
        Cleaned DataFrame.
    """
    df = pd.read_csv(tsv_file_path, sep="\t")
    df = df.iloc[1:]  # Remove the first row

    if table_type == "main_units_tables":
        df = df[~df["land_unit"].str.contains("_summoned")]
        df = df[~df["land_unit"].str.contains("_dummy")]
        df = df[~((df["multiplayer_cost"] == 0) & ~df["caste"].isin(["lord", "hero", "generic"]))]
    
    elif table_type == "character_skill_node_set_items_tables":
        if allowed_patterns:
            df = df[df["item"].str.contains("|".join(allowed_patterns))]
        df = df[~df["item"].str.contains("dummy")]
    
    elif table_type == "character_skill_nodes_tables":
        if allowed_patterns:
            df = df[df["key"].str.contains("|".join(allowed_patterns))]
        df = df[~df["key"].str.contains("dummy")]

    logging.info(f"TSV file '{tsv_file_path}' successfully read and cleaned for table '{table_type}'.")
    return df

def write_updated_tsv_file(data: List[Dict], headers: List[str], version_info: str, target_path: str, file_name: str, allow_duplicates: bool = False):
    """Write the updated TSV file to the target path.

    Args:
        data (List[Dict]): List of dictionaries representing the data to write to the TSV file.
        headers (List[str]): List of headers for the TSV file.
        version_info (str): String containing the version information for the TSV file.
        target_path (str): Path to the target directory where the updated TSV file will be written.
        file_name (str): Name of the TSV file to write.
        allow_duplicates (bool, optional): Whether to allow duplicates in the TSV file. Defaults to False.
    """
    # Create the target directory if it doesn't exist
    os.makedirs(target_path, exist_ok=True)
    
    file_path = f"{target_path}/{file_name}.tsv"
    file_exists = os.path.exists(file_path)
    
    # If file doesn't exist, we need to write headers and version info
    if not file_exists:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("\t".join(headers) + "\n")
            f.write(version_info + "\n")
    
    # Read existing data to check for duplicates if needed
    existing_keys = set()
    if not allow_duplicates and file_exists:
        try:
            existing_data, _, _ = load_tsv_data(file_path)
            existing_keys = {row[headers[0]] for row in existing_data}
        except:
            pass
    
    # Append new data to the file
    with open(file_path, "a", encoding="utf-8") as f:
        for row in data:
            key_column = headers[0]
            if not allow_duplicates and row[key_column] in existing_keys:
                continue
            existing_keys.add(row[key_column])
            # Sometimes the mod's table is outdated. The provided headers is always the latest so it may have new columns that these old tables do not have.
            # In that case, we set the cell to an empty string.
            ordered_values = [row[header] if row.get(header) else "" for header in headers]
            f.write("\t".join(ordered_values) + "\n")

def sort_tsv_data(target_path: str, file_name: str, sort_key: str = None):
    """Sort the data in a TSV file by a specified column.

    Args:
        target_path (str): Path to the directory containing the TSV file.
        file_name (str): Name of the TSV file without the .tsv extension.
        sort_key (str, optional): Column name to sort by. If None, sorts by the first column. Defaults to None.
    """
    file_path = f"{target_path}/{file_name}.tsv"
    if not os.path.exists(file_path):
        logging.error(f"TSV file {file_path} does not exist to sort.")
        return

    # Load the existing data.
    data, headers, version_info = load_tsv_data(file_path)

    # Determine the sort key and defaults to the first column if not specified.
    sort_key = sort_key or headers[0]

    # Sort the data.
    data.sort(key=lambda x: x.get(sort_key, ""))

    # Write the sorted data back to the file.
    with open(file_path, "w", encoding="utf-8") as f:
        # Write headers and version info.
        f.write("\t".join(headers) + "\n")
        f.write(version_info + "\n")

        # Write all data rows and handle missing columns with empty strings.
        for row in data:
            ordered_values = [row.get(header, "") for header in headers]
            f.write("\t".join(ordered_values) + "\n")

def merge_move(source_path: str, destination_path: str):
    """Moves a folder to its destination and overwrite any existing files.
    
    Args:
        source_path (str): The path to the source folder.
        destination_path (str): The path to the destination folder.
    """
    destination_path = os.path.join(destination_path, os.path.basename(source_path))
    os.makedirs(destination_path, exist_ok=True)

    for root, _, files in os.walk(source_path):
        # Determine the relative path to recreate the folder structure.
        relative_path = os.path.relpath(root, source_path)
        destination_dir = os.path.join(destination_path, relative_path)
        os.makedirs(destination_dir, exist_ok=True)

        # Move files to the destination folder while overwriting any existing files.
        for file in files:
            source_file = os.path.join(root, file)
            destination_file = os.path.join(destination_dir, file)
            if os.path.exists(destination_file):
                os.remove(destination_file)
            shutil.move(source_file, destination_file)

    # Remove the source folder afterwards.
    shutil.rmtree(source_path)

def cleanup_folders(folders_to_cleanup: List[str]):
    """Clean up the folders that were created during the extraction process.
    
    Args:
        folders_to_cleanup (List[str]): List of folders to cleanup.
    """
    for folder in folders_to_cleanup:
        if os.path.exists(folder):
            shutil.rmtree(folder)
