-- Chasslo_Landmarks_IEE
local caps = {
    -- Skaven
    {"ChassloIEE_BlackClaws", "special", 1},
    -- Dark Elves
    {"ChassloIee_CrimsonCorsairs", "special", 1},
}

local ttc = core:get_static_object("tabletopcaps")
if ttc then
    ttc.add_setup_callback(function()
        ttc.add_unit_list(caps, true)
    end)
end