# Total War: Warhammer 3 Modding Tools

This repository contains a suite of tools designed to assist me in creating and maintaining my mods for Total War: Warhammer 3. These scripts mainly focus on automating my workflows.

## Important Notes

- **rpfm_cli**: Ensure that `rpfm_cli.exe` is located in the same directory as the scripts. This tool is used for schema updates and data extraction.
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

### 5. `melee.py`
Adjusts melee combat data for units by modifying attack intervals and writing updated data to a new file.

### 6. `velocity.py`
Updates projectile velocity data by adjusting and writing new velocity data for projectiles.

### 7. `120.py`
Modifies data for ranged attacks with a 120-degree arc by updating and writing modified data to a new file.

### 8. `supported_mods.py`
Manages and lists supported mods by providing paths and configurations for various mods.

### 9. `utilities.py`
Provides utility functions for data handling, including functions for loading and cleaning TSV data, used across various scripts.

### 10. `process_main_units_tables.py`
Processes main unit tables for mod integration by loading, cleaning, and extracting data from main unit tables, supporting mod compatibility and updates.
