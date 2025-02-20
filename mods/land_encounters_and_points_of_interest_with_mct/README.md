# Land Encounters And Points Of Interest + MCT Support

This updated mod takes up the work of the original mod author, `diagonal_zero`.

## A few things to note

- The faction data is generated using the `process_main_units_tables.py` from the helper scripts and is expected to be used to keep it up to date for new/updated mods as needed.
- The regex pattern used to sort each unit into specific factions is generalized as many of these mods do not follow a set pattern in their unit key naming.
- Generally removed support for modded factions being spawned in as invasion forces due to needing to tinker with their `startpos`. Failing to do so will result in their lords and heroes spawning in all messed up and glitchy. Thei individual units however are still collected into the `Random Encounter Force Generation System` to be distributed into vanilla factions spawning in as invasion forces.