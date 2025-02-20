"""Script to modify melee attack intervals in melee_weapons TSV files.

Processes TSV files to:
1. Halve melee attack interval values.
2. Preserve data integrity for non-numeric values.
"""

from utilities import load_tsv_data
import logging
import os
import time
from typing import List, Dict


def update_melee_attack_intervals(unit_data: List[Dict]):
    """Adjust melee attack intervals to improve combat responsiveness.
    
    Args:
        unit_data (List[Dict]): List of unit data dictionaries from battle_entities_tables.
        
    Returns:
        List of modified unit data with updated attack intervals.
    """
    modified_data = []
    
    for row in unit_data:
        try:
            current_interval = row["melee_attack_interval"]
            modified_row = row.copy()
            modified_row["melee_attack_interval"] = str(float(current_interval) / 2)
            modified_data.append(modified_row)
        except ValueError:
            logging.warning(f"Invalid interval value: {current_interval} - preserving original")
            modified_data.append(row)
    
    return modified_data

if __name__ == "__main__":
    logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)
    start_time = time.time()
    
    try:
        # Load TSV data.
        # ------------------------------------------------------------------
        unit_data, headers, game_version = load_tsv_data("melee.tsv")
        
        # Apply combat pacing modifications.
        # ------------------------------------------------------------------
        updated_data = update_melee_attack_intervals(unit_data)
        
        # Write modified output.
        # ------------------------------------------------------------------
        os.makedirs(os.path.dirname("new_melee.tsv"), exist_ok=True)
        
        with open("new_melee.tsv", "w", encoding="utf-8") as f:
            f.write("\t".join(headers) + "\n")
            f.write(game_version + "\n")
            
            for row in updated_data:
                ordered_values = [row[header] for header in headers]
                f.write("\t".join(ordered_values) + "\n")
                
        logging.info("Successfully created new_melee.tsv with updated combat pacing")

    except FileNotFoundError as e:
        logging.error(f"Missing required file: {e.filename}")
    except Exception as e:
        logging.exception(e)

    end_time = round(time.time() - start_time, 2)
    logging.info(f"Total time for modifying melee attack intervals: {end_time} seconds or {round(end_time / 60, 2)} minutes.")
