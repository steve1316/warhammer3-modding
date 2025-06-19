-- Vanilla + DLC
local caps = {
    -- Beastmen
    {"wh3_dlc26_bst_inf_khorngors", "special", 1},
    -- Chaos Dwarfs
    {"wh3_dlc23_chd_veh_iron_daemon_3payload_qb", "special", 2},
    -- Dwarfs
    {"wh3_dlc25_dwf_veh_thunderbarge_grungni_mp", "rare", 3},
    -- Greenskins
    {"wh3_dlc26_grn_inf_rugluds_armoured_orcs", "special", 2},
    {"wh3_main_grn_inf_goblins_sword_shield", "core", 1},
    {"wh3_dlc26_grn_cav_mangler_squig", "special", 2},
    {"wh3_main_grn_inf_orc_boyz_spear_shield", "core", 1},
    {"wh3_dlc26_grn_art_bolt_throwa", "special", 2},
    {"wh_dlc06_grn_mon_spider_hatchlings_0", "core", 1},
    {"wh3_dlc26_grn_mon_arachnarok_spider_flinger", "rare", 3},
    {"wh3_dlc26_grn_mon_colossal_squig_ror", "rare", 2},
    {"wh3_dlc26_grn_inf_black_orcs_shield", "special", 2},
    {"wh3_dlc26_grn_mon_colossal_squig", "rare", 2},
    {"wh3_dlc26_grn_art_bolt_throwa_ror", "special", 2},
    -- Khorne
    {"wh3_dlc26_kho_inf_wrathmongers", "special", 3},
    {"wh3_dlc26_kho_mon_bloodbeast_of_khorne", "special", 2},
    {"wh3_dlc26_kho_inf_khorngors", "special", 1},
    {"wh3_dlc26_kho_mon_slaughterbrute", "rare", 3},
    {"wh2_dlc17_kho_mon_ghorgon_ror_0", "rare", 3},
    {"wh3_dlc26_kho_inf_skullreapers", "special", 2},
    {"wh3_dlc26_chs_inf_chosen_mkho_ror", "special", 3},
    {"wh3_dlc26_kho_inf_wrathmongers_ror", "special", 3},
    {"wh3_dlc26_kho_veh_skullcannon_ror", "rare", 2},
    {"wh2_dlc17_bst_mon_ghorgon_boss_0", "rare", 3},
    -- Ogre Kingdoms
    {"wh3_dlc26_ogr_inf_eshin_maneater_ror", "special", 2},
    {"wh3_dlc26_ogr_mon_blood_vultures", "core", 1},
    {"wh3_dlc26_ogr_mon_yhetees", "special", 2},
    {"wh3_dlc26_ogr_mon_thundertusk", "rare", 3},
    {"wh3_dlc26_ogr_mon_yhetees_ror", "special", 2},
    {"wh3_dlc26_ogr_inf_pigback_riders_ror", "core", 1},
    {"wh3_dlc26_ogr_inf_pigback_riders", "core", 1},
    {"wh3_dlc26_ogr_inf_golgfags_maneaters", "special", 3},
    -- Vampire Counts
    {"wh3_main_vmp_inf_grave_guard_2", "special", 1},
    -- Norsca
    {"wh_dlc08_vmp_mon_terrorgheist_boss", "rare", 3},
    {"wh_dlc08_grn_mon_arachnarok_spider_boss", "rare", 3},
    {"wh_dlc08_nor_mon_frost_wyrm_boss", "rare", 3},
    {"wh_dlc08_grn_mon_giant_boss", "rare", 3},
    {"wh_dlc08_chs_mon_dragon_ogre_shaggoth_boss", "rare", 3},
    {"wh_dlc08_wef_forest_dragon_boss", "rare", 3},
    {"wh_dlc08_nor_mon_war_mammoth_boss", "rare", 3},
    {"wh2_dlc10_nor_mon_phoenix_flamespyre_boss", "rare", 3},
    {"wh2_dlc10_skv_mon_hell_pit_abomination_boss", "rare", 3},
    {"wh2_dlc10_lzd_mon_carnosaur_boss", "rare", 3},
    {"wh2_dlc10_def_mon_war_hydra_boss", "rare", 3},
}

local ttc = core:get_static_object("tabletopcaps")
if ttc then
    ttc.add_setup_callback(function()
        ttc.add_unit_list(caps, true)
    end)
end