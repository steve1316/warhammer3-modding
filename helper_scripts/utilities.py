"""Utility functions for Total War Warhammer 3 modding."""

import pandas as pd
import logging
from typing import List


# TSV file structure constants
HEADER_ROW_INDEX = 0
VERSION_ROW_INDEX = 1
DATA_START_ROW = 2

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
