-- 1a_glf_unit_expansion
local caps = {
    -- Skaven
    {"glf_skv_stormfiend_warpfire", "special", 2},
    {"glf_skv_stormfiend_rattling_gun", "special", 2},
    -- Ogre Kingdoms
    {"glf_ogr_ogres_crossbow", "special", 1},
    -- Slaanesh
    {"glf_sla_seekers_of_slaanesh_archers", "special", 2},
    -- Mercenaries
    {"glf_sp_mercenary_dwarf_warrior", "core", 1},
    {"glf_sp_mercenary_handgunners", "core", 1},
    {"glf_sp_war_elephants", "rare", 1},
    {"glf_sp_mercenary_greatswords", "special", 1},
    {"glf_sp_mercenary_crossbowmen", "core", 1},
    {"glf_sp_mercenary_port_guard", "core", 1},
    {"glf_sp_mercenary_rangers", "core", 1},
    {"glf_sp_mercenary_crossbow_cavalry", "special", 1},
    {"glf_sp_black_archers", "special", 1},
    {"glf_sp_mercenary_eshin_maneater", "special", 1},
    {"glf_cth_jade_chariot_crossbow", "special", 1},
    {"glf_sp_mercenary_halberdiers", "core", 1},
}

local ttc = core:get_static_object("tabletopcaps")
if ttc then
    ttc.add_setup_callback(function()
        ttc.add_unit_list(caps, true)
    end)
end