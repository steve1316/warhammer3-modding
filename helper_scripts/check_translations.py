"""Script to check for missing or placeholder text in translation files for Total War: Warhammer 3 modding.

Validates text files from original and translated mods, comparing key counts and content.
"""

import subprocess
import os
import pandas as pd
import logging
import gc
import shutil
import time
from typing import List


mod_paths_to_be_translated = [
    {
        "mod_path": r"C:\SteamLibrary\steamapps\workshop\content\1142710\3297754796\@whc_cth_unit_wuh_7.pack",
        "translation_path": r"C:\SteamLibrary\steamapps\workshop\content\1142710\3392058226\zzz_@whc_cth_unit_wuh_Alternative_English_Translation.pack",
    },
    {
        "mod_path": r"C:\SteamLibrary\steamapps\workshop\content\1142710\2901237965\Zerooz_All_Units.pack",
        "translation_path": r"C:\SteamLibrary\steamapps\workshop\content\1142710\3315737452\Zerooz_English_Translation_corrections.pack",
    },
    {
        "mod_path": r"C:\SteamLibrary\steamapps\workshop\content\1142710\3316985957\archer_fuyuanshan_faction.pack",
        "translation_path": r"C:\SteamLibrary\steamapps\workshop\content\1142710\3317696617\zzz_cth_fuyuanshan_faction_Alternative_English_Translation.pack",
    },
    {
        "mod_path": r"C:\SteamLibrary\steamapps\workshop\content\1142710\2789871157\Great_Harmony_Sentinel.pack",
        "translation_path": r"C:\SteamLibrary\steamapps\workshop\content\1142710\3393724734\zzz_Great_Harmony_Sentinel_Alternative_English_Translation.pack",
    },
    {
        "mod_path": r"C:\SteamLibrary\steamapps\workshop\content\1142710\3061752415\!!YL_binzhong.pack",
        "translation_path": r"C:\SteamLibrary\steamapps\workshop\content\1142710\3318753302\zzz_YL_binzhong_Alternative_English_Translation.pack",
    },
    {
        "mod_path": r"C:\SteamLibrary\steamapps\workshop\content\1142710\2872222879\@Deer24batuoniya.pack",
        "translation_path": r"C:\SteamLibrary\steamapps\workshop\content\1142710\3393724674\zzz_DEER24_Alternative_English_Translation.pack",
    },
    {
        "mod_path": r"C:\SteamLibrary\steamapps\workshop\content\1142710\2859396310\@Deer24diguochuanqi.pack",
        "translation_path": r"C:\SteamLibrary\steamapps\workshop\content\1142710\3393724674\zzz_DEER24_Alternative_English_Translation.pack",
    },
    {
        "mod_path": r"C:\SteamLibrary\steamapps\workshop\content\1142710\2908711955\@Deer24HEF.pack",
        "translation_path": r"C:\SteamLibrary\steamapps\workshop\content\1142710\3393724674\zzz_DEER24_Alternative_English_Translation.pack",
    },
    {
        "mod_path": r"C:\SteamLibrary\steamapps\workshop\content\1142710\2804084630\@DEERKSL.pack",
        "translation_path": r"C:\SteamLibrary\steamapps\workshop\content\1142710\3393724674\zzz_DEER24_Alternative_English_Translation.pack",
    },
    {
        "mod_path": r"C:\SteamLibrary\steamapps\workshop\content\1142710\2789903784\DEER24Cathay.pack",
        "translation_path": r"C:\SteamLibrary\steamapps\workshop\content\1142710\3393724674\zzz_DEER24_Alternative_English_Translation.pack",
    },
]

if os.path.exists("./text_original"):
    for file_path in os.listdir(f"./text_original/"):
        shutil.rmtree(f"./text_original/{file_path}")
if os.path.exists("./text_translation"):
    for file_path in os.listdir(f"./text_translation/"):
        shutil.rmtree(f"./text_translation/{file_path}")

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

def read_text_tsv_with_schema(tsv_file_path: str):
    """Read a TSV file containing text entries, skipping the schema header row.
    
    Args:
        tsv_file_path (str): Path to the TSV file to read
        
    Returns:
        DataFrame containing the text entries
    """
    df = pd.read_csv(tsv_file_path, sep="\t")
    # Skip the schema header row.
    df = df.iloc[1:]
    return df

def compare_translation_entries(table_name: str, df_original: pd.DataFrame, df_translation: pd.DataFrame, mod_name: str):
    """Compare translation entries between original and translated text data.
    
    Performs three key checks:
    1. Identifies keys missing in translation when original has more entries.
    2. Identifies extra keys in translation when it has more entries.
    3. Checks for placeholder text in translations where original has valid text.
    
    Args:
        table_name (str): Name of the table being checked.
        df_original (pd.DataFrame): DataFrame containing original text entries.
        df_translation (pd.DataFrame): DataFrame containing translated text entries.
        mod_name (str): Name of the mod being checked (for error reporting).
        messages (List[str]): List to accumulate validation messages.
        
    Returns:
        Updated list of messages to review regarding the translation consistency.
    """
    # Use sets for fast comparison of keys between original and translation.
    original_keys = set(df_original["key"])
    translation_keys = set(df_translation["key"])
    
    # Check for missing keys in translation (original has more entries).
    if len(df_original) > len(df_translation):
        # Calculate difference using set operations.
        diff_keys = original_keys - translation_keys
        explanation = f"The number of strings is higher than the translation."
        messages = process_key_differences(diff_keys, mod_name, table_name, messages, explanation, is_missing_in_translation=True)
    
    # Check for extra keys in translation (translation has more entries).
    elif len(df_original) < len(df_translation):
        diff_keys = translation_keys - original_keys
        explanation = f"The number of strings is lower than the translation."
        messages = process_key_differences(diff_keys, mod_name, table_name, messages, explanation, is_missing_in_translation=False)
    
    # Check for placeholder texts regardless of key count match.
    messages = check_placeholder_translations(df_original, df_translation, mod_name, messages)
    return messages

def process_key_differences(diff_keys: List[str], mod_name: str, table_name: str, messages: List[str], explanation: str, is_missing_in_translation: bool):
    """Process key differences between original and translation data.
    
    Handles two types of discrepancies:
    - Keys present in original but missing in translation.
    - Extra keys present in translation but missing in original.
    
    Args:
        diff_keys (List[str]): List of keys that differ between versions.
        mod_name (str): Name of the mod being checked (for error reporting).
        table_name (str): Name of the table being checked.
        messages (List[str]): List to accumulate validation messages.
        explanation (str): Context message about the key difference origin.
        is_missing_in_translation (bool): Flag indicating direction of mismatch (True = missing in translation).
        
    Returns:
        Updated list of messages with key difference warnings.
    """
    for key in diff_keys:
        # Skip automatic update keys by mod authors that don't require translation.
        if key.upper() == "UPDATE":
            continue
        
        # Ensure mod name and explanation are only added once per discrepancy group.
        if f"Mod name: {mod_name}" not in messages:
            messages.append("//////////////////////////////////////////////////")
            messages.append(f"Mod name: {mod_name}")
            messages.append(f"Table name: {table_name}")
        if explanation not in messages:
            messages.append(explanation)
        
        # Create appropriate message based on discrepancy direction.
        if is_missing_in_translation:
            message = f"\"{key}\" is in the original but not in the translation."
        else:
            message = f"\"{key}\" is in the translation but not in the original."
            
        messages.append(message)
    if len(messages) > 0:
        messages.append("=========================")
    return messages

def check_placeholder_translations(df_original: pd.DataFrame, df_translation: pd.DataFrame, mod_name: str, messages: List[str]):
    """Check for placeholder text in translations where original has valid text.
    
    Args:
        df_original (pd.DataFrame): DataFrame containing original text entries.
        df_translation (pd.DataFrame): DataFrame containing translated text entries.
        mod_name (str): Name of the mod being checked (for error reporting).
        messages (List[str]): List to accumulate validation messages.
        
    Returns:
        Updated list of messages with placeholder warnings.
    """
    for _, row in df_translation.iterrows():
        # Normalize translated text for consistent comparison
        translated_text = str(row["text"]).strip().lower()
        if translated_text in ["", "placeholder", "nan"]:
            try:
                # Get corresponding original text using the same key.
                original_text = str(df_original[df_original["key"] == row["key"]]["text"].iloc[0]).strip().lower()
                
                # Only flag if original text is valid (non-placeholder and non-empty)
                if original_text not in ["", "placeholder", "nan"]:
                    # Add mod name header if not already present.
                    if mod_name not in messages:
                        messages.append(mod_name)
                    messages.append(f"\"{row['key']}\" is placeholder/empty in the translation but not in the original.")
            except IndexError:
                messages.append(f"Key {row['key']} not found in the original.")
    return messages

def check_text_string_amount_diff(messages: List[str], mod_name: str, is_collection: bool = False, subfolder_name: str = ""):
    """Validate text file counts and content between original and translation directories.
    
    Performs two main checks:
    1. Compares file counts between original and translation directories
    2. Validates content of matching TSV files using multiple path variations
    
    Args:
        messages (List[str]): List to accumulate validation messages.
        mod_name (str): Name of the mod being checked.
        is_collection (bool): Flag indicating if this is a mod collection with subfolders.
        subfolder_name (str): Subdirectory path for translation files (collection mods only).
        
    Returns:
        Updated list of validation messages.
    """
    # Check file count discrepancies for collection mods.
    if is_collection:
        original_count = len(os.listdir("./text_original/text/"))
        translation_count = len(os.listdir(f"./text_translation/text/{subfolder_name}"))
        
        if original_count > translation_count:
            logging.warning("The number of text files from text_original is higher than text_translation.")
        elif original_count < translation_count:
            logging.warning("The number of text files from text_original is lower than text_translation.")
    
    # Validate content of each TSV file pair.
    for root, _, files in os.walk("./text_original/text/"):
        for file_path in files:
            # Handle different translation file naming conventions.
            possible_translation_path_prepends = ["", "@", "@@", "@@@", "!!!", "!!!!!", "!!!!!!", "db/", "db/@", "db/@@", "db/@@@", "db/!!!", "db/!!!!!", "db/!!!!!!"]
            df_original = read_text_tsv_with_schema(f"{root}/{file_path}")
            
            for prepend in possible_translation_path_prepends:
                try:
                    df_translation = read_text_tsv_with_schema(f"./text_translation/text/{subfolder_name}{prepend}{file_path}")
                    logging.info(f"Found the alternative translation file at ./text_translation/text/{subfolder_name}{prepend}{file_path}.")
                    
                    # Compare entries between original and translation.
                    messages = compare_translation_entries(
                        table_name=f"{prepend}{file_path}",
                        df_original=df_original,
                        df_translation=df_translation,
                        mod_name=mod_name,
                        messages=messages
                    )
                    
                    break
                except FileNotFoundError:
                    continue

    return messages

if __name__ == "__main__":
    logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)
    start_time = time.time()
    
    try:
        messages = []
        for mod in mod_paths_to_be_translated:
            # Check if the mod is installed.
            if not os.path.exists(mod["mod_path"]):
                logging.warning(f"Mod {mod['mod_path']} is not installed.")
                continue

            # Extract files from mod packages.
            # ------------------------------------------------------------------
            logging.info(f"Extracting text folder from {mod['mod_path']}...")
            subprocess.run([
                "./rpfm_cli.exe",
                "--game",
                "warhammer_3",
                "pack",
                "extract",
                "--pack-path",
                mod["mod_path"],
                "--tables-as-tsv",
                "./schemas/schema_wh3.ron",
                "--folder-path",
                "text;./text_original"
            ])
            subprocess.run([
                "./rpfm_cli.exe",
                "--game",
                "warhammer_3",
                "pack",
                "extract",
                "--pack-path",
                mod["translation_path"],
                "--tables-as-tsv",
                "./schemas/schema_wh3.ron",
                "--folder-path",
                "text;./text_translation"
            ])
            
            # Grab the mod name from the mod path without the .pack extension.
            mod_name = os.path.basename(mod["mod_path"]).replace('.pack', '')

            # Perform translation validation.
            # ------------------------------------------------------------------
            if "deer" in mod_name.lower():
                # Specially handle Deer24's mods.
                # Remove a @ if it exists at the beginning of the mod name.
                if mod_name.startswith('@'):
                    mod_name = mod_name[1:]
                
                messages = check_text_string_amount_diff(messages, mod_name, is_collection=True, subfolder_name=f"@@@{mod_name}/")
            else:
                messages = check_text_string_amount_diff(messages, mod_name)

            if os.path.exists("./text_original"):
                for file_path in os.listdir(f"./text_original/"):
                    shutil.rmtree(f"./text_original/{file_path}")
            if os.path.exists("./text_translation"):
                for file_path in os.listdir(f"./text_translation/"):
                    shutil.rmtree(f"./text_translation/{file_path}")
            gc.collect()

        # Report final results.
        # ------------------------------------------------------------------
        print("\n\n")
        logging.info("Translation check completed.")
        if len(messages) > 0:
            logging.info("These are the warning messages to check:")
            for message in messages:
                logging.info(message)
    except Exception as e:
        logging.exception(e)

    # Delete the db/, text_original/, and text_translation/ folders.
    if os.path.exists("./db/"):
        shutil.rmtree("./db/")
    if os.path.exists("./text_original/"):
        shutil.rmtree("./text_original/")
    if os.path.exists("./text_translation/"):
        shutil.rmtree("./text_translation/")

    end_time = round(time.time() - start_time, 2)
    logging.info(f"Total time for processing all text .tsv files: {end_time} seconds or {round(end_time / 60, 2)} minutes.")
