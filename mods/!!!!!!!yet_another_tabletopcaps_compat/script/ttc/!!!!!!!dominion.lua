-- dominion
local caps = {
    -- Kislev
    {"dom_vol_legion_01", "core"},
    {"dom_vol_legion_02", "core"},
    {"dom_vol_legion_03", "core"},
    {"dom_vol_legion_04", "core"},
    {"ksl_vanguard", "special", 1},
    {"ksl_charger", "special", 1},
    {"ksl_lightrifle", "special", 1},
    {"ksl_vanguard", "special", 1},
    {"ksl_vanguard", "special", 1},
    {"ksl_vanguard", "special", 1},
    {"ksl_vanguard", "special", 1},
    {"dom_battle_mage_01", "special", 2},
    {"ksl_paladin1hs", "special", 2},
    {"ksl_paladin2hs", "special", 2},
    {"dom_snipers", "special", 2},
    {"ksl_eclipse", "special", 2},
    {"ksl_cavernbear_rider", "special", 2},
    {"ksl_cavernbear_rider_2", "special", 2},
    {"dom_aeronaught", "special", 2},
    {"dom_aerospear", "special", 2},
    {"dom_quad_cannon", "special", 2},
    {"ogr_battlerooks", "special", 3},
    {"ksl_champion", "rare", 1},
    {"ksl_heavyrifle", "rare", 1},
    {"ogr_rookcans", "rare", 2},
    {"ogr_royalrook", "rare", 2},
    {"ogr_royalrookplas", "rare", 2},
    {"ksl_magneticsentinel", "rare", 3},
    {"ksl_runemech", "rare", 3},
    {"dom_warblimp", "rare", 3},
    {"dom_flying_fort", "rare", 3},
    {"dom_pillbox", "rare", 3},
    {"dom_heavy_tank", "rare", 3},
}

local ttc = core:get_static_object("tabletopcaps")
if ttc then
    ttc.add_setup_callback(function()
        ttc.add_unit_list(caps, true)
    end)
end