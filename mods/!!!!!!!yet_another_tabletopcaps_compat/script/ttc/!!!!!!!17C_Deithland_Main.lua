-- 17C_Deithland_Main
local caps = {
    -- Empire
    {"emp_deithguard_axelocks", "special", 1},
    {"emp_deithguard_blasterkeys", "special", 1},
    {"emp_cinderwind_arbalests", "core", 1},
    {"emp_chemlancers_lances", "core", 1},
    {"emp_tillerguns", "special", 1},
    {"emp_danzigers", "special", 1},
    {"emp_mortar_muskets", "special", 1},
    {"emp_gallowdogs", "core", 1},
    {"emp_pyrehulks_volley", "special", 2},
    {"emp_chemlancers_drilling_guns", "special", 2},
    {"emp_pyrehulks_fusilaxe", "special", 2},
    {"emp_hellbores", "special", 1},
    {"emp_fumecorps_bayos", "core", 1},
    {"emp_deithguard_shields", "special", 1},
}

local ttc = core:get_static_object("tabletopcaps")
if ttc then
    ttc.add_setup_callback(function()
        ttc.add_unit_list(caps, true)
    end)
end