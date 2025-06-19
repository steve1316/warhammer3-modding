"""Utility functions for Total War Warhammer 3 modding."""

import pandas as pd
import subprocess
import os
import logging
from typing import List


FILEPATH_TO_VANILLA_DATA_TABLES = r"C:\SteamLibrary\steamapps\common\Total War WARHAMMER III\data\db.pack"

# TSV file structure constants
HEADER_ROW_INDEX = 0
VERSION_ROW_INDEX = 1
DATA_START_ROW = 2

def extract_tsv_data(table_name: str):
    """Extract the TSV data for a given table name from the vanilla data tables.
    
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

    logging.info(f"TSV file(s) for \"{table_name}\" successfully extracted to {extract_path}.")

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
        A tuple of a list of row dictionaries with header keys and the headers.
    """
    merged_data = []
    headers = None
    for file_name in os.listdir(folder_path):
        print(f"Loading TSV file: {file_name}")
        if file_name.endswith(".tsv"):
            data, headers, _ = load_tsv_data(os.path.join(folder_path, file_name))
            print(f"Loaded {len(data)} rows from {file_name}.")
            merged_data.extend(data)
            if headers is None:
                headers = headers
    print(f"Loaded a total of {len(merged_data)} rows.")
    return merged_data, headers

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
