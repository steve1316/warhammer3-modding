"""Modifies projectile velocities in velocity TSV files to improve combat pacing.

Processes TSV files to:
1. Double positive muzzle velocity values
2. Preserve original values for zero/negative entries
3. Maintain TSV structure and data integrity
"""

import logging
import time
from utilities import load_tsv_data
from typing import List, Dict


def adjust_muzzle_velocities(projectile_data: List[Dict]):
    """Double velocity values for valid positive entries.
    
    Args:
        projectile_data: List of projectile data dictionaries.
        
    Returns:
        List of modified projectile data with updated velocities.
    """
    modified = []
    
    for row in projectile_data:
        try:
            velocity = float(row["muzzle_velocity"])
            new_row = row.copy()
            
            if velocity > 0:
                new_row["muzzle_velocity"] = str(velocity * 2)
                logging.info(f"Updated {row['key']} from {velocity} to {new_row['muzzle_velocity']}.")
            else:
                logging.warning(f"Invalid velocity ({velocity}) - preserving original value")
                
            modified.append(new_row)
            
        except (ValueError, KeyError) as e:
            logging.warning(f"Error processing row: {str(e)} - using original data")
            modified.append(row)
    
    return modified

def write_velocity_data(headers: List[str], version: str, data: List[Dict], output_path: str):
    """Write processed velocity data to new TSV file.
    
    Args:
        headers: Column headers from original file
        version: Game version string
        data: Processed projectile data
        output_path: Output file path
    """
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\t".join(headers) + "\n")
            f.write(version + "\n")
            
            for row in data:
                ordered_values = [row[header] for header in headers]
                f.write("\t".join(ordered_values) + "\n")
                
        logging.info(f"Successfully created {output_path} with updated velocities.")
        
    except Exception as e:
        logging.error(f"Error writing output file: {str(e)}")
        raise

if __name__ == "__main__":
    logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)
    start_time = time.time()
    
    try:
        # Load TSV data.
        # ------------------------------------------------------------------
        projectile_data, headers, game_version = load_tsv_data("velocity.tsv")
        
        # Apply velocity modifications.
        # ------------------------------------------------------------------
        modified_data = adjust_muzzle_velocities(projectile_data)
        
        # Write modified output.
        # ------------------------------------------------------------------
        write_velocity_data(headers, game_version, modified_data, "new_velocity.tsv")
        
    except Exception as e:
        logging.exception(e)
        
    end_time = round(time.time() - start_time, 2)
    logging.info(f"Total time for modifying projectile velocities: {end_time} seconds or {round(end_time / 60, 2)} minutes.")
