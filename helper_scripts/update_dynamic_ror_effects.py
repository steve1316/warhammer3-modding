"""Script to automatically add missing effects from mod packfile to dynamic_rors_effects.py."""

import os
import re
import logging
from typing import Dict, List, Set
from utilities import (
    extract_modded_tsv_data,
    load_multiple_tsv_data,
    cleanup_folders,
    STEAM_LIBRARY_DRIVE,
)
from dynamic_rors_effects import SUPPORTED_EFFECTS

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

MOD_PACKFILE_PATH = f"{STEAM_LIBRARY_DRIVE}\\SteamLibrary\\steamapps\\workshop\\content\\1142710\\3278112051\\!!_nanu_dynamic_rors.pack"
TABLE_NAME = "unit_purchasable_effects_tables"
TEMP_EXTRACT_PATH = "./temp_unit_purchasable_effects_tables"
DYNAMIC_RORS_EFFECTS_FILE = "dynamic_rors_effects.py"


def get_all_existing_effects() -> Set[str]:
    """Get all existing effects from SUPPORTED_EFFECTS as a flat set."""
    existing_effects = set()
    for category, effects in SUPPORTED_EFFECTS.items():
        existing_effects.update(effects)
    return existing_effects


def categorize_effect(effect_key: str) -> str:
    """Categorize an effect key based on naming patterns.

    Args:
        effect_key: The effect key to categorize.

    Returns:
        The category name, or "misc" if no pattern matches.
    """
    # Basic patterns
    if effect_key.startswith("nanu_dynamic_ror_basic_all_"):
        return "generic"
    if effect_key.startswith("nanu_dynamic_ror_basic_artillery_"):
        return "artillery"
    if effect_key.startswith("nanu_dynamic_ror_basic_cavalry_"):
        return "cavalry"
    if effect_key.startswith("nanu_dynamic_ror_basic_elite_"):
        return "generic"
    if effect_key.startswith("nanu_dynamic_ror_basic_melee_"):
        return "melee"
    if effect_key.startswith("nanu_dynamic_ror_basic_monster_"):
        return "monster"
    if effect_key.startswith("nanu_dynamic_ror_basic_ranged_"):
        return "ranged"
    if effect_key.startswith("nanu_dynamic_ror_basic_single_entity_"):
        return "generic"

    # Ability patterns
    if effect_key.startswith("nanu_dynamic_ror_ability_all_"):
        return "generic"
    if effect_key.startswith("nanu_dynamic_ror_ability_melee_"):
        return "melee"
    if effect_key.startswith("nanu_dynamic_ror_ability_powder_"):
        return "ranged"
    if effect_key.startswith("nanu_dynamic_ror_ability_ranged_"):
        return "ranged"
    if effect_key.startswith("nanu_dynamic_ror_ability_single_entity_"):
        return "generic"

    # Attribute patterns
    if effect_key.startswith("nanu_dynamic_ror_attribute_all_"):
        return "generic"
    if effect_key.startswith("nanu_dynamic_ror_attribute_melee_"):
        return "melee"
    if effect_key.startswith("nanu_dynamic_ror_attribute_ranged_"):
        return "ranged"

    # Contact patterns
    if effect_key.startswith("nanu_dynamic_ror_contact_all_"):
        return "generic"
    if effect_key.startswith("nanu_dynamic_ror_contact_ranged_"):
        return "ranged"

    # Ranged ammo type patterns
    if effect_key.startswith("nanu_dynamic_ror_ranged_ammo_type_"):
        return "ranged"
    if effect_key.startswith("nanu_dynamic_ror_scripted_ammo_type_"):
        return "ranged"

    # Climate patterns
    if effect_key.startswith("nanu_dynamic_ror_climate_"):
        return "generic"

    # Special patterns - forces of order
    if "special_forces_of_order_enemy_ability_all_" in effect_key:
        return "anti_order_generic"
    if "special_forces_of_order_enemy_ability_melee_" in effect_key:
        return "anti_order_melee"
    if "special_forces_of_order_enemy_ability_ranged_" in effect_key:
        return "anti_order_ranged"
    if "special_forces_of_order_enemy_contact_all_" in effect_key:
        return "anti_order_generic"
    if "special_forces_of_order_enemy_attribute_melee_" in effect_key:
        return "anti_order_melee"

    # Special patterns - forces of destruction
    if "special_forces_of_destruction_enemy_ranged_ability_" in effect_key:
        return "anti_destruction_ranged"

    # Special patterns - chaos
    if "special_chaos_enemy_melee_" in effect_key:
        return "anti_destruction_melee"
    if "special_chaos_enemy_ranged_" in effect_key:
        return "anti_destruction_ranged"
    if "special_chaos_enemy_powder_" in effect_key:
        return "anti_destruction_ranged"

    # Special patterns - enemy types (generic)
    if re.search(r"special_\w+_enemy_all_", effect_key):
        return "generic"
    if re.search(r"special_\w+_enemy_melee_", effect_key):
        return "melee"
    if re.search(r"special_\w+_enemy_ranged_", effect_key):
        return "ranged"
    if re.search(r"special_\w+_enemy_powder_", effect_key):
        return "ranged"

    # Special patterns - ally types
    if re.search(r"special_\w+_ally_all_", effect_key):
        return "generic"
    if re.search(r"special_\w+_ally_melee_", effect_key):
        return "melee"
    if re.search(r"special_\w+_ally_ranged_", effect_key):
        return "ranged"
    if re.search(r"special_\w+_ally_powder_", effect_key):
        return "ranged"
    if re.search(r"special_\w+_ally_cavalry_", effect_key):
        return "cavalry"

    # Faction-specific patterns - check for direct faction prefixes first
    if effect_key.startswith("nanu_dynamic_ror_cathay_"):
        if "_ability_melee_" in effect_key or "_ability_all_" in effect_key or "_attribute_all_" in effect_key:
            if "_melee_" in effect_key:
                return "cathay_melee"
            return "cathay_generic"
    # Special cathay patterns
    if "special_cathay_ally_ability_melee_" in effect_key:
        return "cathay_melee"
    if "special_cathay_ally_ability_ranged_" in effect_key:
        return "ranged"  # Generic ranged category
    if "special_cathay_enemy_ability_melee_" in effect_key:
        return "melee"  # Generic melee category
    if "special_cathay_enemy_contact_all_" in effect_key:
        return "generic"
    if effect_key.startswith("nanu_dynamic_ror_chaos_"):
        if "_ability_melee_" in effect_key:
            return "chaos_melee"
        if "_daemon_ability_" in effect_key:
            return "chaos_generic"
        if "_contact_" in effect_key:
            return "generic"
    if effect_key.startswith("nanu_dynamic_ror_chorf_"):
        if "_ability_melee_" in effect_key:
            return "melee"  # chorf melee effects go to generic melee
        if "_ability_all_" in effect_key:
            return "generic"
    if effect_key.startswith("nanu_dynamic_ror_dwarf_") or effect_key.startswith("nanu_dynamic_ror_dwarfs_"):
        if "_ability_melee_" in effect_key:
            return "dwarfs_melee"
        if "_ability_powder_" in effect_key or "_ability_ranged_" in effect_key:
            return "dwarfs_ranged"
        if "_ability_all_" in effect_key:
            return "dwarfs_generic"
    if effect_key.startswith("nanu_dynamic_ror_empire_"):
        if "_ability_melee_" in effect_key or "_special_melee_" in effect_key:
            return "empire_melee"
        if "_ability_swordsmen_" in effect_key:  # Swordsmen are melee units
            return "empire_melee"
        if "_basic_knight_" in effect_key:
            return "empire_cavalry"
        if "_attribute_all_" in effect_key or "_attribute_ranged_" in effect_key or "_ability_all_" in effect_key:
            return "empire_generic"
        if "_basic_archer_" in effect_key:
            return "generic"  # Basic archer effects go to generic
        if "_special_" in effect_key:
            return "empire_generic"
    if effect_key.startswith("nanu_dynamic_ror_greenskin_"):
        if "_ability_melee_" in effect_key:
            return "greenskins_melee"
        if "_ability_all_" in effect_key:
            return "greenskins_generic"
    if effect_key.startswith("nanu_dynamic_ror_high_elf_"):
        if "_ability_ranged_" in effect_key:
            return "ranged"  # High elf ranged effects go to generic ranged
    if effect_key.startswith("nanu_dynamic_ror_khorne_"):
        if "_ability_melee_" in effect_key:
            return "khorne_melee"
        if "_ability_monster_" in effect_key or "_ability_bloodthirster_" in effect_key:
            return "khorne_monster"
        if "_ability_all_" in effect_key:
            return "khorne_generic"
        if "_attribute_melee_" in effect_key:
            return "khorne_melee"
    if effect_key.startswith("nanu_dynamic_ror_kislev_"):
        if "_ability_melee_" in effect_key:
            return "kislev_melee"
        if "_ability_ranged_" in effect_key:
            return "kislev_ranged"
    if effect_key.startswith("nanu_dynamic_ror_nurgle_"):
        if "_ability_melee_" in effect_key:
            return "nurgle_melee"
        if "_ability_monster_" in effect_key or "_ability_single_entity_" in effect_key:
            if "_monster_" in effect_key:
                return "nurgle_monster"
            return "nurgle_generic"
        if "_ability_all_" in effect_key:
            return "nurgle_generic"
        if "_special_death_explosion_" in effect_key:
            return "nurgle_generic"
        if "_basic_" in effect_key:
            return "nurgle_generic"
    if effect_key.startswith("nanu_dynamic_ror_ogre_"):
        if "_ability_melee_" in effect_key:
            return "ogre_melee"
    if effect_key.startswith("nanu_dynamic_ror_skaven_"):
        if "_ability_melee_" in effect_key:
            return "skaven_melee"
        if "_ability_all_" in effect_key or "_contact_all_" in effect_key:
            return "skaven_generic"
        if "_death_explosion_" in effect_key:
            return "skaven_generic"
    if effect_key.startswith("nanu_dynamic_ror_slaanesh_"):
        if "_ability_melee_" in effect_key:
            return "slaanesh_melee"
        if "_basic_" in effect_key:
            return "generic"  # Basic slaanesh effects go to generic
    if effect_key.startswith("nanu_dynamic_ror_tzeentch_"):
        if "_ability_melee_" in effect_key:
            return "tzeentch_melee"
        if "_ability_all_" in effect_key or "_attribute_all_" in effect_key:
            return "tzeentch_generic"
        if "_ability_lord_of_change_" in effect_key:
            return "tzeentch_generic"
    
    # Legacy faction-specific patterns (for backward compatibility)
    if "ability_cathay_" in effect_key:
        if "_melee_" in effect_key:
            return "cathay_melee"
        return "cathay_generic"
    if "ability_dwarf_" in effect_key:
        if "_melee_" in effect_key:
            return "dwarfs_melee"
        if "_ranged_" in effect_key or "powder_" in effect_key:
            return "dwarfs_ranged"
        return "dwarfs_generic"
    if "ability_empire_" in effect_key:
        if "_melee_" in effect_key:
            return "empire_melee"
        if "_cavalry_" in effect_key:
            return "empire_cavalry"
        return "empire_generic"
    if "ability_greenskin_" in effect_key:
        if "_melee_" in effect_key:
            return "greenskins_melee"
        return "greenskins_generic"
    if "ability_khorne_" in effect_key:
        if "_melee_" in effect_key:
            return "khorne_melee"
        if "_monster_" in effect_key:
            return "khorne_monster"
        return "khorne_generic"
    if "ability_kislev_" in effect_key:
        if "_melee_" in effect_key:
            return "kislev_melee"
        if "_ranged_" in effect_key:
            return "kislev_ranged"
    if "ability_nurgle_" in effect_key:
        if "_melee_" in effect_key:
            return "nurgle_melee"
        if "_monster_" in effect_key:
            return "nurgle_monster"
        return "nurgle_generic"
    if "ability_ogre_" in effect_key:
        if "_melee_" in effect_key:
            return "ogre_melee"
    if "ability_skaven_" in effect_key:
        if "_melee_" in effect_key:
            return "skaven_melee"
        return "skaven_generic"
    if "ability_slaanesh_" in effect_key:
        if "_melee_" in effect_key:
            return "slaanesh_melee"
    if "ability_tzeentch_" in effect_key:
        if "_melee_" in effect_key:
            return "tzeentch_melee"
        return "tzeentch_generic"

    # Lizardmen patterns
    if "lizard_ability_" in effect_key or "lizard_contact_" in effect_key or "lizard_attribute_" in effect_key:
        if "_melee_" in effect_key:
            return "lizardmen_melee"
        return "lizardmen_generic"

    # Bretonnia patterns
    if "contact_bretonnia_" in effect_key or "bretonnia_special_" in effect_key:
        return "bretonnia_artillery"
    
    # Death explosion patterns - these are generic effects
    if "death_explosion_all_" in effect_key:
        return "generic"
    
    # Special nurgle patterns
    if "special_nurgle_all_" in effect_key:
        return "nurgle_generic"
    
    # If no pattern matches, return misc
    return "misc"


def read_dynamic_rors_effects_file() -> str:
    """Read the dynamic_rors_effects.py file as text."""
    with open(DYNAMIC_RORS_EFFECTS_FILE, "r", encoding="utf-8") as f:
        return f.read()


def insert_effects_into_category(file_content: str, category: str, effects: List[str]) -> str:
    """Insert multiple effects into a category in alphabetical order.

    Args:
        file_content: The file content as a string.
        category: The category name.
        effects: List of effect keys to insert.

    Returns:
        Updated file content.
    """
    if not effects:
        return file_content

    # Find the category section - look for the category key and its list
    # Pattern: "category": [ ... ]
    category_start_pattern = rf'    "{re.escape(category)}": \['
    match = re.search(category_start_pattern, file_content)

    if not match:
        # Category doesn't exist, need to add it before the closing brace
        # Find the last closing bracket before the final }
        last_bracket_pos = file_content.rfind("    ],")
        if last_bracket_pos != -1:
            # Insert new category after the last category
            insert_pos = file_content.find("\n", last_bracket_pos) + 1
            indented_effects = [f'        "{e}",' for e in sorted(effects)]
            new_category = f'    "{category}": [\n' + "\n".join(indented_effects) + "\n    ],\n"
            file_content = file_content[:insert_pos] + new_category + file_content[insert_pos:]
        else:
            # Fallback: insert before final }
            insert_pos = file_content.rfind("}")
            indented_effects = [f'        "{e}",' for e in sorted(effects)]
            new_category = f'    "{category}": [\n' + "\n".join(indented_effects) + "\n    ],\n"
            file_content = file_content[:insert_pos] + new_category + file_content[insert_pos:]
        return file_content

    # Find the start of the list content (after the opening bracket)
    list_start = match.end()

    # Find the end of this category's list (the closing bracket and comma)
    # We need to find the matching closing bracket, accounting for nested brackets
    bracket_count = 1
    pos = list_start
    list_end = -1

    while pos < len(file_content) and bracket_count > 0:
        if file_content[pos] == "[":
            bracket_count += 1
        elif file_content[pos] == "]":
            bracket_count -= 1
            if bracket_count == 0:
                list_end = pos
                break
        pos += 1

    if list_end == -1:
        logging.warning(f"Could not find end of category {category}, skipping insertion")
        return file_content

    # Extract the list content
    list_content = file_content[list_start:list_end]

    # Extract all existing effects in this category
    effect_pattern = r'"([^"]+)"'
    existing_effects = re.findall(effect_pattern, list_content)

    # Add the new effects and sort
    for effect in effects:
        if effect not in existing_effects:
            existing_effects.append(effect)
    existing_effects.sort()

    # Rebuild the category content with proper indentation
    indented_effects = [f'        "{e}",' for e in existing_effects]
    new_list_content = "\n".join(indented_effects)

    # Replace the list content
    new_file_content = file_content[:list_start] + "\n" + new_list_content + "\n" + file_content[list_end:]

    return new_file_content


def write_dynamic_rors_effects_file(content: str):
    """Write the updated content to dynamic_rors_effects.py."""
    with open(DYNAMIC_RORS_EFFECTS_FILE, "w", encoding="utf-8") as f:
        f.write(content)


def main():
    """Main function to extract, compare, and add missing effects."""
    logging.info("Starting missing effects detection and addition process.")

    # Step 1: Extract effect bundles from mod packfile
    logging.info(f"Extracting {TABLE_NAME} from mod packfile...")
    extract_modded_tsv_data(TABLE_NAME, MOD_PACKFILE_PATH, TEMP_EXTRACT_PATH)

    # Step 2: Load and merge all TSV files
    tsv_folder_path = os.path.join(TEMP_EXTRACT_PATH, f"db/{TABLE_NAME}")
    if not os.path.exists(tsv_folder_path):
        logging.error(f"Extracted folder not found: {tsv_folder_path}")
        return

    logging.info(f"Loading and merging TSV files from {tsv_folder_path}...")
    merged_data, headers, version_info = load_multiple_tsv_data(tsv_folder_path)

    # Step 3: Filter for relevant effects and compare
    logging.info("Filtering and comparing effects...")

    # Check what the actual key column name is (case-insensitive)
    key_column = None
    for h in headers:
        if h.lower() == "key":
            key_column = h
            break

    if not key_column:
        logging.error(f"Could not find 'Key' column. Available columns: {headers}")
        cleanup_folders([TEMP_EXTRACT_PATH])
        return

    mod_effects = set()
    for row in merged_data:
        key = row.get(key_column, "")
        if key.startswith("nanu_dynamic_ror_"):
            mod_effects.add(key)

    existing_effects = get_all_existing_effects()
    missing_effects = mod_effects - existing_effects

    logging.info(f"Found {len(mod_effects)} total nanu_dynamic_ror_* effects in mod.")
    logging.info(f"Found {len(existing_effects)} existing effects in SUPPORTED_EFFECTS.")
    logging.info(f"Found {len(missing_effects)} missing effects to add.")

    if not missing_effects:
        logging.info("No missing effects found. Nothing to add.")
        cleanup_folders([TEMP_EXTRACT_PATH])
        return

    # Step 4: Categorize missing effects
    logging.info("Categorizing missing effects...")
    categorized_effects: Dict[str, List[str]] = {}
    for effect in missing_effects:
        category = categorize_effect(effect)
        if category not in categorized_effects:
            categorized_effects[category] = []
        categorized_effects[category].append(effect)

    # Log categorization results
    for category, effects in sorted(categorized_effects.items()):
        logging.info(f"  {category}: {len(effects)} effects")

    # Step 5: Add missing effects to file
    logging.info("Adding missing effects to dynamic_rors_effects.py...")
    file_content = read_dynamic_rors_effects_file()

    # Insert all effects for each category at once
    for category, effects in categorized_effects.items():
        file_content = insert_effects_into_category(file_content, category, effects)
        logging.info(f"  Added {len(effects)} effects to {category}")

    write_dynamic_rors_effects_file(file_content)
    logging.info("Successfully updated dynamic_rors_effects.py")

    # Step 6: Recategorize any misc effects
    logging.info("Recategorizing misc effects...")
    file_content = read_dynamic_rors_effects_file()
    
    # Check if misc category exists
    misc_pattern = r'    "misc": \[(.*?)(?=\n    "[^"]+": \[|\n\})'
    misc_match = re.search(misc_pattern, file_content, re.DOTALL)
    
    if misc_match:
        misc_content = misc_match.group(1)
        effect_pattern = r'"([^"]+)"'
        misc_effects = re.findall(effect_pattern, misc_content)
        
        if misc_effects:
            logging.info(f"Found {len(misc_effects)} effects in misc category to recategorize.")
            recategorized: Dict[str, List[str]] = {}
            still_misc: List[str] = []
            
            for effect in misc_effects:
                new_category = categorize_effect(effect)
                if new_category == "misc":
                    still_misc.append(effect)
                else:
                    if new_category not in recategorized:
                        recategorized[new_category] = []
                    recategorized[new_category].append(effect)
            
            if recategorized:
                # Remove effects from misc category
                if still_misc:
                    # Update misc category with remaining effects
                    indented_effects = [f'        "{e}",' for e in sorted(still_misc)]
                    new_misc_content = "\n".join(indented_effects)
                    file_content = (
                        file_content[:misc_match.start(1)]
                        + "\n" + new_misc_content + "\n"
                        + file_content[misc_match.end(1):]
                    )
                else:
                    # Remove misc category entirely
                    full_misc_pattern = r'    "misc": \[.*?\],\n'
                    file_content = re.sub(full_misc_pattern, "", file_content, flags=re.DOTALL)
                
                # Add effects to their new categories
                for category, effects in recategorized.items():
                    file_content = insert_effects_into_category(file_content, category, effects)
                    logging.info(f"  Recategorized {len(effects)} effects from misc to {category}")
                
                write_dynamic_rors_effects_file(file_content)
                logging.info("Successfully recategorized misc effects.")
            else:
                logging.info("No misc effects needed recategorization.")
        else:
            logging.info("Misc category is empty, removing it.")
            # Remove empty misc category
            full_misc_pattern = r'    "misc": \[.*?\],\n'
            file_content = re.sub(full_misc_pattern, "", file_content, flags=re.DOTALL)
            write_dynamic_rors_effects_file(file_content)

    # Step 7: Cleanup
    logging.info("Cleaning up temporary files...")
    cleanup_folders([TEMP_EXTRACT_PATH])
    logging.info("Process completed successfully.")


if __name__ == "__main__":
    main()
