"""Script to modify unit fire arc values in battle_entities_tables TSV files for Total War Warhammer 3 modding.

Processes a TSV file containing unit stats and ensures ranged units have at least 120 degree firing arcs.
"""

from utilities import load_tsv_data
import logging
import time
import os
from typing import List, Dict


def update_rows_for_120_degree_ranged_attacks(joined_data: List[Dict]):
    """Adjust fire arc values for ranged units to ensure minimum 120 degree coverage.
    
    Args:
        joined_data (List[Dict]): List of dictionaries representing unit data rows from battle_entities_tables db.
        
    Returns:
        Modified list with updated fire_arc_close values where applicable.
    """
    # Only modifies values between 0 and 120 (exclusive).
    # Preserves existing 0, negative, or values >= 120.
    for row in joined_data:
        current_arc = float(row["fire_arc_close"])
        if 0 < current_arc < 120:
            row["fire_arc_close"] = "120"
            logging.info(f"Updated {row['key']} from {current_arc} to 120 degrees.")
    return joined_data

if __name__ == "__main__":
    logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)
    start_time = time.time()
    
    try:
        # Load TSV data.
        # ------------------------------------------------------------------
        mod_data, headers, game_version_line = load_tsv_data("120.tsv")
        
        # Apply fire arc modifications.
        # ------------------------------------------------------------------
        updated_data = update_rows_for_120_degree_ranged_attacks(mod_data)
        
        # Write modified data to new TSV.
        # ------------------------------------------------------------------
        with open('new_120.tsv', 'w') as f:
            # Maintain original header structure.
            f.write('\t'.join(headers) + '\n')
            f.write(game_version_line + '\n')
            
            # Write updated rows while preserving column order.
            for row in updated_data:
                ordered_values = [row[header] for header in headers]
                f.write('\t'.join(ordered_values) + '\n')

    except Exception as e:
        logging.exception(e)

    end_time = round(time.time() - start_time, 2)
    logging.info(f"Total time for modifying fire arc values: {end_time} seconds or {round(end_time / 60, 2)} minutes.")
