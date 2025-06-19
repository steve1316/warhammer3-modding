# Total War: Warhammer 3 Modding Tools

This repository contains a suite of tools designed to assist me in creating and maintaining my mods for Total War: Warhammer 3. These scripts mainly focus on automating my workflows.

## Important Notes

- **rpfm_cli**: Ensure that `rpfm_cli.exe` from https://github.com/Frodo45127/rpfm is located in the same directory as the scripts. This tool is used for schema updates and data extraction.
- **schemas**: Ensure that the `schemas` are downloaded from https://github.com/Frodo45127/rpfm-schemas and placed in a `/schemas` folder in the same directory as the scripts and `rpfm_cli.exe`.
- **TSV Files**: Some scripts require specific TSV files to be pre-extracted and placed in the same directory as the scripts. Ensure these files are available before running the scripts.

## Scripts Overview

### 1. `check_translations.py`
Ensures translation files are complete and accurate by comparing original and translated files to verify consistency.

### 2. `check_new_rows.py`
Identifies discrepancies between original and modded data files by comparing two data files to find missing entries in the modded version.

### 3. `glf_inner_join.py`
Merges and updates unit data for mods by combining data from different sources and updating specific attributes.

### 4. `correct_quotation_marks.py`
Standardizes quotation mark usage in localization files by correcting and ensuring proper formatting of quotes in text files.

### 5. `supported_mods.py`
Manages and lists supported mods by providing paths and configurations for various mods.

### 6. `utilities.py`
Provides utility functions for data handling, including functions for loading and cleaning TSV data, used across various scripts.

### 7. `process_main_units_tables.py`
Processes main unit tables for mod integration by loading, cleaning, and extracting data from main unit tables, supporting mod compatibility and updates.

### 8. `update_supported_mods_list.py`
Generates a formatted list of supported mods that have their melee, firing arcs and projectile velocity data adjusted. The lists are to be updated in their respective Steam Workshop pages whenever a new mod is added or removed.

### 9. `update_modified_attribute_mods.py`
Script to update the modified attribute mods from the Steam Workshop to account for latest changes to the vanilla and modded data tables.