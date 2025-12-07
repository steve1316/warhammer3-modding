"""This update script is used to perform the following tasks:
1. Update the faction data for the land encounters mod.
2. Update the Dynamic RoR mod.
3. Update the modified attribute mods.
"""

import logging
import time
import subprocess
import signal
from typing import List


def run_script(cmd: List[str]):
    """Runs a script and returns the exit code.

    Args:
        cmd (List[str]): The command to run.

    Returns:
        The exit code of the script.
    """
    p = subprocess.Popen(cmd)
    try:
        return p.wait()
    except KeyboardInterrupt:
        p.send_signal(signal.SIGINT)
        p.wait()
        raise


if __name__ == "__main__":
    logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)
    start_time = time.time()

    # Update the faction data for the land encounters mod.
    logging.info("Updating the faction data for the land encounters mod...")
    run_script(["python", "process_main_units_tables.py"])

    # Update the Dynamic RoR mod.
    logging.info("Updating the Dynamic RoR mod...")
    run_script(["python", "update_dynamic_rors.py"])

    # Update the modified attribute mods.
    run_script(["python", "update_modified_attribute_mods.py"])

    end_time = round(time.time() - start_time, 2)
    logging.info(f"Total time for updating: {end_time} seconds or {round(end_time / 60, 2)} minutes.")
