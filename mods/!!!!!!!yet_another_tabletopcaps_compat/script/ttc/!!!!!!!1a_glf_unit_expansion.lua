-- 1a_glf_unit_expansion
local caps = {
    -- Skaven
    {"glf_skv_stormfiend_warpfire", "special", 2},
    {"glf_skv_stormfiend_rattling_gun", "special", 2},
}

local ttc = core:get_static_object("tabletopcaps")
if ttc then
    ttc.add_setup_callback(function()
        ttc.add_unit_list(caps, true)
    end)
end