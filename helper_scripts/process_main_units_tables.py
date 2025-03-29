"""Processes Total War: Warhammer 3 unit data from TSV files into faction-specific JSON/Lua outputs.

Key functionalities:
1. Extracts and transforms unit data from game files.
2. Handles vanilla and modded content through configurable patterns.
3. Generates both JSON and Lua representations of faction data.
"""

import subprocess
import os
import pandas as pd
import json
import logging
import gc
import shutil
import time
from utilities import read_and_clean_tsv
from supported_mods import SUPPORTED_MODS
from typing import List, Dict


FAILED_MODS = []
MISSING_MODS = []

# Delete all folders inside "./db".
if os.path.exists("./db"):
    for file_path in os.listdir(f"./db/"):
        shutil.rmtree(f"./db/{file_path}")

# If "./schemas" does not exist, download the schemas.
if not os.path.exists("./schemas"):
    logging.info("Downloading schemas...")
    subprocess.run([
        "./rpfm_cli.exe", 
        "--game", 
        "warhammer_3", 
        "schemas", 
        "update", 
        "--schema-path", 
        "./schemas"
    ])

    # Now convert them to JSON.
    subprocess.run([
        "./rpfm_cli.exe", 
        "--game", 
        "warhammer_3", 
        "schemas", 
        "to-json", 
        "--schemas-path", 
        "./schemas"
    ])

# =====================================================================================
# Configuration Constants
# =====================================================================================

# These are the faction keys acquired from "db/cultures_subcultures_tables".
faction_keys = [
    # {"neu": "neu"},
    {"tmb": "tmb"}, 
    {"cst": "cst"}, 
    {"def": "def"}, 
    {"hef": "hef"}, 
    {"lzd": "lzd"}, 
    {"skv": "skv"}, 
    {"chd": "chd"}, 
    {"kho": "kho"}, 
    {"ksl": "ksl"}, 
    {"tze": "tze"}, 
    {"cth": "cth"}, 
    # {"dae": "dae"},  
    {"nur": "nur"}, 
    {"ogr": "ogr"}, 
    {"sla": "sla"}, 
    {"bst": "bst"}, 
    {"wef": "wef"}, 
    {"nor": "nor"}, 
    {"brt": "brt"}, 
    {"chs": "chs"}, 
    {"dwf": "dwf"}, 
    {"emp": "emp"}, 
    {"grn": "grn"}, 
    {"vmp": "vmp"}
]

allowed_character_skill_key_patterns = [
    "_army_",
    "_generic_",
    "_magic_",
    "_unique_",
    "_self_",
    "_personal_",
    "_ability_",
    "_misc_",
    "_battle_",
    "_ranged_",
    "_combat_",
]

# =====================================================================================
# Core Data Processing Functions
# =====================================================================================

def dict_to_lua_table(data_dict: Dict, indent: int = 0):
    """Convert Python dictionary to Warhammer modding-friendly Lua table format.
    
    Args:
        data_dict (Dict): Nested dictionary of faction data.
        indent (int, optional): Current indentation level for pretty-printing. Defaults to 0.
        
    Returns:
        Lua table string ready for file output.
    """
    # Check if the dictionary is empty.
    if not data_dict:
        return "{}"

    lua_str = "{\n"
    for key, value in data_dict.items():
        lua_str += " " * (indent + 4)
        if isinstance(key, str):
            lua_str += f'["{key}"] = '
        else:
            lua_str += f"[{key}] = "

        if isinstance(value, dict):
            lua_str += dict_to_lua_table(value, indent + 4)
        elif isinstance(value, list):
            # Check if the list is empty.
            if not value:
                lua_str += "{}"
            else:
                # Check if the list contains only strings.
                if all(isinstance(item, str) for item in value):
                    lua_str += "{ " + ", ".join(f'"{item}"' for item in value) + " }"
                else:
                    lua_str += "{\n"
                    for item in value:
                        lua_str += " " * (indent + 8) + "{"
                        if isinstance(item, dict):
                            # Handle allowed_lords and character_skill_overrides.
                            if "land_unit" in item:
                                lua_str += f'land_unit="{item["land_unit"]}"'
                                if "agent_subtype" in item:
                                    lua_str += f', agent_subtype="{item["agent_subtype"]}"'
                                if "agent_type" in item:
                                    lua_str += f', agent_type="{item["agent_type"]}"'
                                if "origin" in item:
                                    lua_str += f', origin="{item["origin"]}"'
                                if "recruitment_cost" in item:
                                    lua_str += f', recruitment_cost={item["recruitment_cost"]}'
                                if "multiplayer_cost" in item:
                                    lua_str += f', multiplayer_cost={item["multiplayer_cost"]}'
                                if "skill_overrides" in item:
                                    lua_str += ', skill_overrides={ ' + ", ".join(f'"{skill}"' for skill in item["skill_overrides"]) + ' }'
                            else:
                                lua_str += ", ".join(f'{k}="{v}"' for k, v in item.items())
                        else:
                            lua_str += f'"{item}"'
                        lua_str += "},\n"
                    lua_str += " " * (indent + 4) + "}"
        else:
            lua_str += f'"{value}"'
        lua_str += ",\n"
    lua_str += " " * indent + "}"
    return lua_str

def process_tsv_files(directory: str, table_type: str, allowed_patterns: List[str] = None):
    """Process TSV files in a directory, read, clean, and merge them into a single DataFrame.
    
    Args:
        directory (str): Directory containing TSV files.
        table_type (str): Type of the table to determine cleaning rules.
        allowed_patterns (List[str], optional): Patterns to allow in specific columns.
        
    Returns:
        Merged and cleaned DataFrame.
    """
    merged_df = pd.DataFrame()
    if os.path.exists(directory):
        for file_path in os.listdir(directory):
            temp_df = read_and_clean_tsv(os.path.join(directory, file_path), table_type, allowed_patterns)
            merged_df = pd.concat([merged_df, temp_df])
        merged_df = merged_df.drop_duplicates()
    return merged_df

def tsv_to_faction_data(
    factions_data: Dict, 
    faction_keys: List[str], 
    df_main_units_tables: pd.DataFrame, 
    df_faction_agent_permitted_subtypes: pd.DataFrame, 
    df_character_skill_node_set_items: pd.DataFrame, 
    df_character_skill_node_sets: pd.DataFrame, 
    df_character_skill_nodes: pd.DataFrame, 
    default_faction: str = None, 
    do_not_use_underscore_pattern: bool = False
    ):
    """Transform TSV data into structured faction data dictionary.
    
    Args:
        factions_data (Dict): Existing data to augment.
        faction_keys (List[str]): Faction detection patterns.
        df_main_units_tables (pd.DataFrame): Processed units data.
        df_faction_agent_permitted_subtypes (pd.DataFrame): Allowed agent subtypes.
        df_character_skill_node_set_items (pd.DataFrame): Skill node items data.
        df_character_skill_node_sets (pd.DataFrame): Skill node sets data.
        df_character_skill_nodes (pd.DataFrame): Skill nodes data.
        default_faction (str): Fallback faction if none detected.
        do_not_use_underscore_pattern (bool): Disable underscore pattern matching.
        
    Returns:
        Updated factions data with new units and skills.
    """
    try:
        # Usage in the main code
        if mod["name"].replace(".pack", "") != "vanilla":
            df_main_units_tables = process_tsv_files("./db/main_units_tables/", "main_units_tables")
            df_faction_agent_permitted_subtypes = process_tsv_files("./db/faction_agent_permitted_subtypes_tables/", "faction_agent_permitted_subtypes")
            df_character_skill_node_set_items = process_tsv_files(
                "./db/character_skill_node_set_items_tables/", 
                "character_skill_node_set_items_tables", 
                allowed_patterns=allowed_character_skill_key_patterns
            )
            df_character_skill_node_sets = process_tsv_files("./db/character_skill_node_sets_tables/", "character_skill_node_sets_tables")
            df_character_skill_nodes = process_tsv_files(
                "./db/character_skill_nodes_tables/", 
                "character_skill_nodes_tables", 
                allowed_patterns=allowed_character_skill_key_patterns
            )
        
        # Iterate over each unit row in the DataFrame
        for _, row in df_main_units_tables.iterrows():
            if default_faction:
                _, faction_value = default_faction, default_faction
            elif do_not_use_underscore_pattern:
                faction_key, faction_value = next(
                    ((key, faction[key]) for faction in faction_keys for key in faction if f"{key}" in row["land_unit"]), (None, None)
                )
            else:
                faction_key, faction_value = next(
                    (
                        (key, faction[key])
                        for faction in faction_keys
                        for key in faction
                        if f"_{key}_" in row["land_unit"]
                    ),
                    (None, None),
                )
            if faction_value is None:
                logging.warning(f"No valid faction key found for land unit '{row['land_unit']}' for faction_key: {faction_key}")
                continue

            # Check if the extracted faction key is in any of the dictionaries in faction_keys
            if not any(faction_value in faction_dict for faction_dict in faction_keys):
                logging.warning(f"Faction key '{faction_value}' not recognized for land unit '{row['land_unit']}'")
                continue

            logging.info(f"Processing {row['land_unit']} for faction {faction_value}...")

            # Initialize the faction and tier if they don't exist.
            if faction_value not in factions_data:
                factions_data[faction_value] = {"units": {"tier_0": {}, "tier_1": {}, "tier_2": {}, "tier_3": {}, "tier_4": {}, "tier_5": {}}}
                # Initialize categories within each tier
                for tier in factions_data[faction_value]["units"]:
                    factions_data[faction_value]["units"][tier] = {
                        "melee_infantry": [],
                        "missile_infantry": [],
                        "melee_cavalry": [],
                        "missile_cavalry": [],
                        "monstrous_infantry": [],
                        "monstrous_cavalry": [],
                        "chariot": [],
                        "warmachine": [],
                        "war_beast": [],
                        "monster": [],
                        "generic": [],
                        "lord": [],
                        "hero": [],
                    }

            # Save the unit data.
            tier = f"tier_{int(row['tier'])}"
            caste_category = row["caste"]
            if caste_category in factions_data[faction_value]["units"][tier]:
                # Save lords and heroes into their own lists.
                if caste_category != "lord" and caste_category != "hero":
                    factions_data[faction_value]["units"][tier][caste_category].append(
                        {
                            "land_unit": row["land_unit"],
                            "recruitment_cost": int(row["recruitment_cost"]),
                            "multiplayer_cost": int(row["multiplayer_cost"]),
                            "origin": mod["name"].replace(".pack", ""),
                        }
                    )

                # Check if the unit key is in the allowed_lords field.
                if (
                    "character_overrides" in mod 
                    and faction_value in mod["character_overrides"] 
                ):
                    for key_substring in ["lords", "heroes"]:
                        if f"allowed_{key_substring}" not in factions_data[faction_value]:
                            factions_data[faction_value][f"allowed_{key_substring}"] = []
                        
                        if f"allowed_{key_substring}" in mod["character_overrides"][faction_value]:
                            for allowed_object in mod["character_overrides"][faction_value][f"allowed_{key_substring}"]:
                                if row["land_unit"] == allowed_object["land_unit"]:
                                    logging.info(f"Adding {row['land_unit']} to allowed_{key_substring} for faction {faction_value}.")
                                    new_allowed_object = {
                                        "land_unit": allowed_object["land_unit"],
                                        "agent_subtype": allowed_object["agent_subtype"],
                                        "origin": mod["name"].replace(".pack", ""),
                                        "skill_overrides": [],
                                    }
                                    
                                    # Use the character_skill_node_sets_tables to grab key by referencing its agent_subtype_key with the agent_subtype from the allowed_object.
                                    agent_subtype = allowed_object["agent_subtype"]
                                    df_character_skill_node_sets_key = df_character_skill_node_sets.loc[df_character_skill_node_sets["agent_subtype_key"] == agent_subtype, "key"].values[0]
                                    
                                    # Inside character_skill_node_set_items_tables, all skill rows for a character belong to a set which is the key from the previous step.
                                    df_character_skill_node_set_items_skills = df_character_skill_node_set_items.loc[df_character_skill_node_set_items["set"] == df_character_skill_node_sets_key, "item"].values
                                    
                                    # Now from each skill row, grab all the skill keys from character_skill_nodes_tables by referencing the key column and then grabbing the value from the character_skill_key column.
                                    skills = []
                                    try:
                                        for skill_node in df_character_skill_node_set_items_skills:
                                            skill_node_skill_key = df_character_skill_nodes.loc[df_character_skill_nodes["key"] == skill_node, "character_skill_key"].values[0]
                                            skills.append(skill_node_skill_key)
                                    except:
                                        pass
                                    
                                    # Save the skills.
                                    new_allowed_object["skill_overrides"] = skills
                                    
                                    # Check if the agent_subtype for heroes is in the df_agent_permitted_subtypes DataFrame.
                                    if new_allowed_object["agent_subtype"] in df_faction_agent_permitted_subtypes["subtype"].values:
                                        # Retrieve the corresponding agent value.
                                        agent_value = df_faction_agent_permitted_subtypes.loc[
                                            df_faction_agent_permitted_subtypes["subtype"] == new_allowed_object["agent_subtype"], "agent"
                                        ].values[0]
                                        new_allowed_object["agent_type"] = agent_value
                                    
                                    factions_data[faction_value][f"allowed_{key_substring}"].append(new_allowed_object)
    except Exception as e:
        FAILED_MODS.append(mod["name"])
        logging.exception(e)

    return factions_data

# =====================================================================================
# Main Execution Flow
# =====================================================================================

if __name__ == "__main__":
    logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)
    start_time = time.time()

    # Create a list of all the mods that are supported from SUPPORTED_MODS in the "name" field.
    # supported_mods = [mod["name"].replace(".pack", "") for mod in SUPPORTED_MODS]
    # print(json.dumps(supported_mods, indent=4))
    # exit()

    try:
        factions_data = {}
        
        # Load vanilla data foundations.
        # ------------------------------------------------------------------
        df_main_units_tables_vanilla = read_and_clean_tsv(
            f"./vanilla_main_units_tables.tsv", 
            "main_units_tables"
        )
        df_faction_agent_permitted_subtypes_vanilla = read_and_clean_tsv(
            f"./vanilla_faction_agent_permitted_subtypes_tables.tsv", 
            "faction_agent_permitted_subtypes"
        )
        df_character_skill_node_set_items_vanilla = read_and_clean_tsv(
            f"./vanilla_character_skill_node_set_items_tables.tsv", 
            "character_skill_node_set_items_tables"
        )
        df_character_skill_node_sets_vanilla = read_and_clean_tsv(
            f"./vanilla_character_skill_node_sets_tables.tsv", 
            "character_skill_node_sets_tables"
        )
        df_character_skill_nodes_vanilla = read_and_clean_tsv(
            f"./vanilla_character_skill_nodes_tables.tsv", 
            "character_skill_nodes_tables"
        )
        
        # Conver the schemas from Ron to JSON.
        subprocess.run([
            "./rpfm_cli.exe",
            "--game",
            "warhammer_3",
            "schemas",
            "to-json",
            "--schemas-path",
            "./schemas"
        ])

        # Load the schema.
        with open("schemas/schema_wh3.json", "r", encoding="utf-8") as schema_file:
            schema = json.load(schema_file)

        # Process supported mods.
        # ------------------------------------------------------------------
        for mod in SUPPORTED_MODS:
            # Check if the mod is installed.
            if mod["path"] and not os.path.exists(mod["path"]):
                MISSING_MODS.append(mod["name"])
                continue

            # Extract mod data.
            # ------------------------------------------------------------------
            if mod["name"] != "vanilla":
                logging.info(f"Extracting mod data from {mod['name']}...")
                
                # Loop through each folder path and run the extraction command.
                folders_to_extract = [
                    "db/main_units_tables",
                    "db/faction_agent_permitted_subtypes_tables",
                    "db/character_skill_node_set_items_tables",
                    "db/character_skill_node_sets_tables",
                    "db/character_skill_nodes_tables"
                ]
                for folder in folders_to_extract:
                    subprocess.run([
                        "./rpfm_cli.exe",
                        "--game",
                        "warhammer_3",
                        "pack",
                        "extract",
                        "--pack-path",
                        mod["path"],
                        "--tables-as-tsv",
                        "./schemas/schema_wh3.ron",
                        "--folder-path",
                        f"{folder};./"
                    ])

            # Transform data.
            # ------------------------------------------------------------------
            if mod["name"] == "vanilla":
                logging.info(f"Processing vanilla units...")
                factions_data = tsv_to_faction_data(
                    factions_data, 
                    faction_keys, 
                    df_main_units_tables_vanilla, 
                    df_faction_agent_permitted_subtypes_vanilla, 
                    df_character_skill_node_set_items_vanilla, 
                    df_character_skill_node_sets_vanilla, 
                    df_character_skill_nodes_vanilla
                )
            else:
                logging.info(f"Now processing {mod['name']}...")

                default_faction = None
                do_not_use_underscore_pattern = False
                pattern_overrides = mod["pattern_overrides"]
                if "*" in pattern_overrides:
                    default_faction = pattern_overrides["*"]
                    logging.info(f"Pattern is the wildcard itself so we will use '{default_faction}' for all units in this mod.")
                elif any("*" in key for key in pattern_overrides):
                    logging.info(f"Pattern is a wildcard pattern, so we will not use the underscore pattern.")
                    do_not_use_underscore_pattern = True

                # If the mod has a factions_override field, add the contents to faction_keys.
                if "faction_overrides" in mod:
                    for new_faction_key in mod["faction_overrides"]:
                        faction_keys.append({new_faction_key: new_faction_key})
                temp_faction_keys = faction_keys.copy()

                if pattern_overrides and "*" not in pattern_overrides:
                    for temp_faction_key, temp_faction_value in pattern_overrides.items():
                        temp_faction_keys.append({temp_faction_key.replace("*", ""): temp_faction_value})
                        if "_" in temp_faction_key:
                            do_not_use_underscore_pattern = True

                factions_data = tsv_to_faction_data(
                    factions_data, 
                    temp_faction_keys, 
                    df_main_units_tables_vanilla, 
                    df_faction_agent_permitted_subtypes_vanilla, 
                    df_character_skill_node_set_items_vanilla, 
                    df_character_skill_node_sets_vanilla, 
                    df_character_skill_nodes_vanilla, 
                    default_faction=default_faction, 
                    do_not_use_underscore_pattern=do_not_use_underscore_pattern
                )

            # Delete all folders inside "./db".
            if os.path.exists("./db"):
                for file_path in os.listdir(f"./db/"):
                    shutil.rmtree(f"./db/{file_path}")
            gc.collect()

        # Write output files.
        # ------------------------------------------------------------------
        with open("factions_data.json", "w", encoding="utf-8") as json_file:
            json.dump(factions_data, json_file, indent=4)

        # Convert the factions_data to Lua table format.
        lua_data = "return " + dict_to_lua_table(factions_data)

        # Save the Lua table to a file.
        with open("factions_data.lua", "w", encoding="utf-8") as lua_file:
            lua_file.write(lua_data)
    except Exception as e:
        logging.exception(e)

    if MISSING_MODS:
        logging.info(f"Missing mods: {MISSING_MODS}")
    if FAILED_MODS:
        logging.info(f"Failed mods: {FAILED_MODS}")

    end_time = round(time.time() - start_time, 2)
    logging.info(f"Total time for processing all main_units_tables .tsv files: {end_time} seconds or {round(end_time / 60, 2)} minutes.")
