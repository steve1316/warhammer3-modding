"""Script to generate a formatted list of supported mods that have their melee, firing arcs and projectile velocity data adjusted.
The lists are to be updated in their respective Steam Workshop pages whenever a new mod is added or removed.
"""

import logging
import time
from datetime import datetime
from supported_mods import SUPPORTED_MODS


if __name__ == "__main__":
    logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)
    start_time = time.time()

    list_of_mods_for_melee = []
    list_of_mods_for_ranged_arc = []
    list_of_mods_for_velocity = []

    for mod in SUPPORTED_MODS:
        if mod["package_name"] == "vanilla":
            continue
        mod_id = mod["path"].split("/")[-2]
        list_item = f"[*] [url=https://steamcommunity.com/sharedfiles/filedetails/?id={mod_id}]{mod['name']}[/url]"
        if "melee" in mod["modified_attributes"]:
            list_of_mods_for_melee.append(list_item)
        if "ranged_arc" in mod["modified_attributes"]:
            list_of_mods_for_ranged_arc.append(list_item)
        if "velocity" in mod["modified_attributes"]:
            list_of_mods_for_velocity.append(list_item)

    for type in ["melee", "ranged_arc", "velocity"]:
        text_body = f"""[h1]Quick Overview[/h1]
Auto-generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} via Python script.

[list]

INSERT_LIST_HERE

[/list]
"""

        list_of_mods = list_of_mods_for_melee if type == "melee" else list_of_mods_for_ranged_arc if type == "ranged_arc" else list_of_mods_for_velocity
        text_body = text_body.replace(f"INSERT_LIST_HERE", "\n".join(list_of_mods))
        with open(f"supported_mods_list_to_update_{type}.txt", "w", encoding="utf-8") as f:
            f.write(text_body)

    end_time = round(time.time() - start_time, 2)
    logging.info(f"Total time for generating updated lists of supported mods: {end_time} seconds or {round(end_time / 60, 2)} minutes.")
