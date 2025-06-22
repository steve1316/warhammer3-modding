"""Script to update the dynamic RORs for Nanu from the Steam Workshop to account for latest changes to modded data tables."""

from utilities import extract_tsv_data, load_tsv_data, extract_modded_tsv_data, load_multiple_tsv_data, write_updated_tsv_file, merge_move
from supported_mods import SUPPORTED_MODS
from dynamic_rors_effects import SUPPORTED_EFFECTS
import time
import os
import shutil
import subprocess
import logging
from typing import Dict, Any
import gc


MISSING_MODS = []

# Faction keys are found in groupings_military_tables.

CHAOS_FACTIONS = [
    "wh_main_group_chaos",
    "wh3_main_dae",
    "wh3_main_group_belakor",
    "wh3_main_kho",
    "wh3_main_nur",
    "wh3_main_pro_kho",
    "wh3_main_pro_tze",
    "wh3_main_sla",
    "wh3_main_tze",
    "wh3_dlc20_group_chs_azazel",
    "wh3_dlc20_group_chs_festus",
    "wh3_dlc20_group_chs_valkia",
    "wh3_dlc20_group_chs_vilitch",
    "wh3_dlc25_nur_tamurkhan",
]

EMPIRE_SPECIFIC_FACTIONS = [
    "wh_main_group_empire",
    "wh_main_group_empire_golden_order",
    "wh_main_group_empire_reikland",
    "wh3_dlc25_group_elspeth",
]

HIGH_ELF_SPECIFIC_FACTIONS = [
    "wh2_main_hef",
    "wh2_main_hef_imrik",
]

KISLEV_SPECIFIC_FACTIONS = [
    "wh3_main_ksl",
    "wh3_main_pro_ksl",
]

GREENSKINS_SPECIFIC_FACTIONS = [
    "wh_main_group_greenskins",
    "wh_main_group_savage_orcs",
    "wh2_dlc12_grn_leaf_cutterz_tribe",
]

NORSCA_SPECIFIC_FACTIONS = [
    "wh_main_group_norsca",
    "wh_main_group_norsca_steppe",
]

DARK_ELF_SPECIFIC_FACTIONS = [
    "wh2_main_def",
    "wh3_main_def_morathi",
]

SKAVEN_SPECIFIC_FACTIONS = [
    "wh2_main_skv",
    "wh2_main_skv_ikit",
]

TOMB_KINGS_SPECIFIC_FACTIONS = [
    "wh2_dlc09_tomb_kings",
    "wh2_dlc09_tomb_kings_arkhan",
]

VAMPIRE_COAST_SPECIFIC_FACTIONS = [
    "wh2_dlc11_group_vampire_coast",
    "wh2_dlc11_group_vampire_coast_sartosa",
    "wh2_dlc11_cst_harpoon_the_sunken_land_corsairs",
    "wh2_dlc11_cst_shanty_dragon_spine_privateers",
    "wh2_dlc11_cst_shanty_middle_sea_brigands",
    "wh2_dlc11_cst_shanty_shark_straight_seadogs",
]

KHORNE_SPECIFIC_FACTIONS = [
    "wh3_main_kho",
    "wh3_main_pro_kho",
    "wh3_dlc20_group_chs_valkia",
]

NURGLE_SPECIFIC_FACTIONS = [
    "wh3_main_nur",
    "wh3_dlc20_group_chs_festus",
    "wh3_dlc25_nur_tamurkhan",
]

SLAANESH_SPECIFIC_FACTIONS = [
    "wh3_main_sla",
    "wh3_dlc20_group_chs_azazel",
]

TZEENTCH_SPECIFIC_FACTIONS = [
    "wh3_main_tze",
    "wh3_main_pro_tze",
    "wh3_dlc20_group_chs_vilitch",
]

ANTI_ORDER_FACTIONS = [
    "wh_main_group_chaos",
    "wh_main_group_greenskins",
    "wh_main_group_norsca",
    "wh_main_group_norsca_steppe",
    "wh_main_group_savage_orcs",
    "wh_main_group_vampire_counts",
    "wh_dlc03_group_beastmen",
    "wh2_main_def",
    "wh2_main_skv",
    "wh2_main_skv_ikit",
    "wh2_dlc09_tomb_kings",
    "wh2_dlc09_tomb_kings_arkhan",
    "wh2_dlc11_group_vampire_coast",
    "wh2_dlc11_group_vampire_coast_sartosa",
    "wh2_dlc11_cst_harpoon_the_sunken_land_corsairs",
    "wh2_dlc11_cst_shanty_dragon_spine_privateers",
    "wh2_dlc11_cst_shanty_middle_sea_brigands",
    "wh2_dlc11_cst_shanty_shark_straight_seadogs",
    "wh2_dlc12_grn_leaf_cutterz_tribe",
    "wh2_dlc16_group_drycha",
    "wh3_main_dae",
    "wh3_main_def_morathi",
    "wh3_main_group_belakor",
    "wh3_main_kho",
    "wh3_main_nur",
    "wh3_main_ogr",
    "wh3_main_pro_kho",
    "wh3_main_pro_tze",
    "wh3_main_sla",
    "wh3_main_tze",
    "wh3_dlc20_group_chs_azazel",
    "wh3_dlc20_group_chs_festus",
    "wh3_dlc20_group_chs_valkia",
    "wh3_dlc20_group_chs_vilitch",
    "wh3_dlc23_group_chaos_dwarfs",
    "wh3_dlc25_nur_tamurkhan",
]

ANTI_DESTRUCTION_FACTIONS = [
    "wh_main_group_bretonnia",
    "wh_main_group_dwarfs",
    "wh_main_group_empire",
    "wh_main_group_empire_golden_order",
    "wh_main_group_empire_reikland",
    "wh_main_group_kislev",
    "wh_main_group_teb",
    "wh_dlc05_group_wood_elves",
    "wh2_main_hef",
    "wh2_main_hef_imrik",
    "wh2_main_lzd",
    "wh3_main_cth",
    "wh3_main_ksl",
    "wh3_main_pro_ksl",
    "wh3_dlc25_group_elspeth",
]


def add_anti_order_generic_effects(faction: str):
    """Add anti-order generic effects based on faction.

    Args:
        faction (str): The faction of the unit.
    """
    unit_effects = []
    if faction in ANTI_ORDER_FACTIONS:
        unit_effects += SUPPORTED_EFFECTS["anti_order_generic"]

        if faction in GREENSKINS_SPECIFIC_FACTIONS:
            unit_effects += SUPPORTED_EFFECTS["greenskins_generic"]
        elif faction in SKAVEN_SPECIFIC_FACTIONS:
            unit_effects += SUPPORTED_EFFECTS["skaven_generic"]
        elif faction in CHAOS_FACTIONS:
            unit_effects += SUPPORTED_EFFECTS["chaos_generic"]
            if faction in KHORNE_SPECIFIC_FACTIONS:
                unit_effects += SUPPORTED_EFFECTS["khorne_generic"]
            elif faction in NURGLE_SPECIFIC_FACTIONS:
                unit_effects += SUPPORTED_EFFECTS["nurgle_generic"]
            elif faction in TZEENTCH_SPECIFIC_FACTIONS:
                unit_effects += SUPPORTED_EFFECTS["tzeentch_generic"]
    
    return unit_effects

def add_anti_destruction_generic_effects(faction: str):
    """Add anti-destruction generic effects based on faction.

    Args:
        faction (str): The faction of the unit.
    """
    unit_effects = []
    if faction in ANTI_DESTRUCTION_FACTIONS:
        if faction == "wh3_main_cth":
            unit_effects += SUPPORTED_EFFECTS["cathay_generic"]
        elif faction == "wh_main_group_dwarfs":
            unit_effects += SUPPORTED_EFFECTS["dwarfs_generic"]
        elif faction in EMPIRE_SPECIFIC_FACTIONS:
            unit_effects += SUPPORTED_EFFECTS["empire_generic"]
        elif faction == "wh2_main_lzd":
            unit_effects += SUPPORTED_EFFECTS["lizardmen_generic"]

    return unit_effects

def add_melee_effects(faction: str):
    """Add melee effects.

    Args:
        faction (str): The faction of the unit.
    """
    unit_effects = []
    unit_effects += SUPPORTED_EFFECTS["melee"]

    if faction in ANTI_ORDER_FACTIONS:
        unit_effects += SUPPORTED_EFFECTS["anti_order_melee"]

        if faction in CHAOS_FACTIONS:
            unit_effects += SUPPORTED_EFFECTS["chaos_melee"]

        if faction in GREENSKINS_SPECIFIC_FACTIONS:
            unit_effects += SUPPORTED_EFFECTS["greenskins_melee"]
        elif faction == "wh3_main_ogr":
            unit_effects += SUPPORTED_EFFECTS["ogre_melee"]
        elif faction in SKAVEN_SPECIFIC_FACTIONS:
            unit_effects += SUPPORTED_EFFECTS["skaven_melee"]
        elif faction in KHORNE_SPECIFIC_FACTIONS:
            unit_effects += SUPPORTED_EFFECTS["khorne_melee"]
        elif faction in NURGLE_SPECIFIC_FACTIONS:
            unit_effects += SUPPORTED_EFFECTS["nurgle_melee"]
        elif faction in SLAANESH_SPECIFIC_FACTIONS:
            unit_effects += SUPPORTED_EFFECTS["slaanesh_melee"]
        elif faction in TZEENTCH_SPECIFIC_FACTIONS:
            unit_effects += SUPPORTED_EFFECTS["tzeentch_melee"]
    elif faction in ANTI_DESTRUCTION_FACTIONS:
        unit_effects += SUPPORTED_EFFECTS["anti_destruction_melee"]

        if faction == "wh3_main_cth":
            unit_effects += SUPPORTED_EFFECTS["cathay_melee"]
        elif faction == "wh_main_group_dwarfs":
            unit_effects += SUPPORTED_EFFECTS["dwarfs_melee"]
        elif faction in EMPIRE_SPECIFIC_FACTIONS:
            unit_effects += SUPPORTED_EFFECTS["empire_melee"]
        elif faction in KISLEV_SPECIFIC_FACTIONS:
            unit_effects += SUPPORTED_EFFECTS["kislev_melee"]
        elif faction == "wh2_main_lzd":
            unit_effects += SUPPORTED_EFFECTS["lizardmen_melee"]

    return unit_effects

def add_ranged_effects(faction: str):
    """Add ranged effects.

    Args:
        faction (str): The faction of the unit.
    """
    unit_effects = []
    unit_effects += SUPPORTED_EFFECTS["ranged"]

    if faction in ANTI_ORDER_FACTIONS:
        unit_effects += SUPPORTED_EFFECTS["anti_order_ranged"]
    elif faction in ANTI_DESTRUCTION_FACTIONS:
        unit_effects += SUPPORTED_EFFECTS["anti_destruction_ranged"]

        if faction == "wh_main_group_dwarfs":
            unit_effects += SUPPORTED_EFFECTS["dwarfs_ranged"]
        elif faction in KISLEV_SPECIFIC_FACTIONS:
            unit_effects += SUPPORTED_EFFECTS["kislev_ranged"]

    return unit_effects

def add_artillery_effects(faction: str):
    """Add artillery effects.

    Args:
        faction (str): The faction of the unit.
    """
    unit_effects = []
    unit_effects += SUPPORTED_EFFECTS["artillery"]

    if faction == "wh_main_group_bretonnia":
        unit_effects += SUPPORTED_EFFECTS["bretonnia_artillery"]

    return unit_effects

def add_cavalry_effects(faction: str):
    """Add cavalry effects.

    Args:
        faction (str): The faction of the unit.
    """
    unit_effects = []
    unit_effects += SUPPORTED_EFFECTS["cavalry"]

    if faction in EMPIRE_SPECIFIC_FACTIONS:
        unit_effects += SUPPORTED_EFFECTS["empire_cavalry"]

    return unit_effects

def add_monster_effects(faction: str):
    """Add monster effects.

    Args:
        faction (str): The faction of the unit.
    """
    unit_effects = []
    unit_effects += SUPPORTED_EFFECTS["monster"]

    if faction in KHORNE_SPECIFIC_FACTIONS:
        unit_effects += SUPPORTED_EFFECTS["khorne_monster"]
    elif faction in NURGLE_SPECIFIC_FACTIONS:
        unit_effects += SUPPORTED_EFFECTS["nurgle_monster"]

    return unit_effects

def process_unit_by_category(unit_data: Dict[str, Any], main_units_mapping: Dict[str, Any], faction: str):
    """Process a unit based on its category and assign appropriate effects.

    Args:
        unit_data (Dict[str, Any]): The unit data.
        main_units_mapping (Dict[str, Any]): The mapping of unit keys to their main_units_tables data.
        faction (str): The faction of the unit.

    Returns:
        A list of strings representing the effects to add to the unit.
    """
    # Ignore Lords and Heroes.
    if unit_data["class"] == "com":
        return []
    logging.info(f"Processing unit {unit_data['key']} in category {unit_data['category']} for faction {faction}.")
    category = unit_data["category"]
    # This needs to be initialized to an empty list to avoid memory conflicts that causes Python to keep the old list in memory.
    unit_effects = []
    unit_effects += SUPPORTED_EFFECTS["generic"]
    unit_effects += add_anti_order_generic_effects(faction)
    unit_effects += add_anti_destruction_generic_effects(faction)

    if category == "artillery":
        unit_effects += add_ranged_effects(faction)
        unit_effects += add_artillery_effects(faction)
    elif category == "cavalry" and int(unit_data["primary_ammo"]) > 0:
        unit_effects += add_ranged_effects(faction)
        unit_effects += add_cavalry_effects(faction)
    elif category == "cavalry" or category == "war_beast":
        unit_effects += add_melee_effects(faction)
        unit_effects += add_cavalry_effects(faction)
    elif category == "war_machine" and int(unit_data["primary_ammo"]) > 0:
        unit_effects += add_ranged_effects(faction)
        unit_effects += add_artillery_effects(faction)
    elif category == "war_machine":
        unit_effects += add_melee_effects(faction)
    elif category == "inf_melee":
        unit_effects += add_melee_effects(faction)
    elif category == "inf_ranged":
        unit_effects += add_ranged_effects(faction)
    elif category == "monster":
        unit_effects += add_melee_effects(faction)
        unit_effects += add_monster_effects(faction)

    if unit_data["key"] in main_units_mapping and int(main_units_mapping[unit_data["key"]]["num_men"]) > 1:
        for single_entity_effect in [
            "nanu_dynamic_ror_basic_single_entity_1",
            "nanu_dynamic_ror_basic_single_entity_2",
            "nanu_dynamic_ror_basic_single_entity_3",
            "nanu_dynamic_ror_ability_single_entity_slime_trail",
            "nanu_dynamic_ror_ability_nurgle_single_entity_slime_trail",
            "nanu_dynamic_ror_ability_nurgle_single_entity_spurting_acid_blood",
            "nanu_dynamic_ror_ability_nurgle_single_entity_spurting_bile_blood",
        ]:
            try:
                unit_effects.remove(single_entity_effect)
            except ValueError:
                pass

    # Sort the effects by name ascending.
    unit_effects.sort()

    return unit_effects

if __name__ == "__main__":
    logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)
    start_time = time.time()

    try:
        # Extract the vanilla unit_purchasable_effect_sets_tables data.
        extract_tsv_data("unit_purchasable_effect_sets_tables")
        _, vanilla_unit_purchasable_effect_sets_tables_headers, vanilla_unit_purchasable_effect_sets_tables_version_info = load_tsv_data("vanilla_unit_purchasable_effect_sets_tables/db/unit_purchasable_effect_sets_tables/data__.tsv")
        for mod in SUPPORTED_MODS:
            # Check if the mod is installed.
            if mod["path"] and not os.path.exists(mod["path"]):
                MISSING_MODS.append(mod["package_name"])
                continue
            if mod["package_name"] == "vanilla":
                continue

            logging.info(f"Processing {mod['package_name']}...")

            # Table names cannot end in numbers.
            folder_name = mod["package_name"].replace(".pack", "").replace(" ", "_")
            if folder_name[-1].isdigit():
                folder_name = folder_name[:-1]

            # Extract the units_to_groupings_military_permissions_tables and main_units_tables data from this mod.
            extract_modded_tsv_data("units_to_groupings_military_permissions_tables", mod["path"], f"./modded_units_to_groupings_military_permissions_tables")
            extract_modded_tsv_data("main_units_tables", mod["path"], f"./modded_main_units_tables")
            if not os.path.exists("./modded_units_to_groupings_military_permissions_tables"):
                logging.warning(f"No modded units to groupings military permissions tables found for {mod['package_name']}.")
                continue

            # Load the modded data from the tables that were just extracted and create mappings via unit keys.
            merged_modded_units_to_military_permissions_data, _ = load_multiple_tsv_data(f"./modded_units_to_groupings_military_permissions_tables/db/units_to_groupings_military_permissions_tables")
            merged_modded_main_units_data, _ = load_multiple_tsv_data(f"./modded_main_units_tables/db/main_units_tables")
            units_to_factions_mapping = {}
            main_units_mapping = {}
            for data in merged_modded_units_to_military_permissions_data:
                units_to_factions_mapping[data["unit"]] = data["military_group"]
            for data in merged_modded_main_units_data:
                main_units_mapping[data["unit"]] = data

            # Extract the modded land_units_tables data.
            extract_modded_tsv_data("land_units_tables", mod["path"], f"./modded_land_units_tables")
            merged_modded_land_units_data, _ = load_multiple_tsv_data(f"./modded_land_units_tables/db/land_units_tables")

            unit_purchasable_effect_sets_tables_data = []
            for data in merged_modded_land_units_data:
                faction = units_to_factions_mapping.get(data["key"])
                if not faction:
                    continue

                # Collect all possible effects for the unit.
                for effect in process_unit_by_category(data, main_units_mapping, faction):
                    unit_purchasable_effect_sets_tables_data.append(
                        {
                            "unit": data["key"],
                            "purchasable_effect": effect,
                            "is_exclusive": "False",
                        }
                    )

            if len(unit_purchasable_effect_sets_tables_data) > 0:
                # Write the updated unit_purchasable_effect_sets_tables data.
                unit_purchasable_effect_sets_tables_version_info = vanilla_unit_purchasable_effect_sets_tables_version_info.replace(
                    "data__", f"!!!{folder_name}"
                )
                write_updated_tsv_file(
                    unit_purchasable_effect_sets_tables_data,
                    vanilla_unit_purchasable_effect_sets_tables_headers,
                    unit_purchasable_effect_sets_tables_version_info,
                    "",
                    "./!!!!!!!_nanu_dynamic_rors_compat/db/unit_purchasable_effect_sets_tables",
                    f"!!!{folder_name}",
                )

            for cleanup_dir in [
                "./modded_units_to_groupings_military_permissions_tables",
                "./modded_land_units_tables",
                "./modded_main_units_tables",
            ]:
                if os.path.exists(cleanup_dir):
                    shutil.rmtree(cleanup_dir)

            gc.collect()
    except Exception as e:
        logging.exception(e)

    # After processing all mods, move the mod folder to the destination folder.
    if os.path.exists("./!!!!!!!_nanu_dynamic_rors_compat"):
        logging.info(f"Moving !!!!!!!_nanu_dynamic_rors_compat to ../mods/.")
        merge_move("./!!!!!!!_nanu_dynamic_rors_compat", "../mods/")

    # Use the RPFM CLI to delete the files from the packfile's unit_purchasable_effect_sets_tables folder.
    subprocess.run([
        "./rpfm_cli.exe", 
        "--game", 
        "warhammer_3", 
        "pack",
        "delete",
        "--pack-path",
        r"C:\SteamLibrary\steamapps\common\Total War WARHAMMER III\data\!!!!!!!_nanu_dynamic_rors_compat.pack",
        "--folder-path",
        "db/unit_purchasable_effect_sets_tables"
    ])
    # Then merge the updated mod files into the packfile.
    subprocess.run([
        "./rpfm_cli.exe",
        "--game",
        "warhammer_3",
        "pack",
        "add",
        "--pack-path",
        r"C:\SteamLibrary\steamapps\common\Total War WARHAMMER III\data\!!!!!!!_nanu_dynamic_rors_compat.pack",
        "--tsv-to-binary",
        "./schemas/schema_wh3.ron",
        "--folder-path",
        "../mods/!!!!!!!_nanu_dynamic_rors_compat/db/unit_purchasable_effect_sets_tables;db/unit_purchasable_effect_sets_tables"
    ])

    # Perform final cleanup.
    if os.path.exists("./vanilla_unit_purchasable_effect_sets_tables"):
        shutil.rmtree("./vanilla_unit_purchasable_effect_sets_tables")

    if MISSING_MODS:
        logging.info(f"Missing mods: {MISSING_MODS}")

    end_time = round(time.time() - start_time, 2)
    logging.info(f"Total time: {end_time} seconds or {round(end_time / 60, 2)} minutes.")
