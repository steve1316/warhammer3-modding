-- DEER24Cathay
local caps = {
    -- Grand Cathay
    {"WWD_baochuan", "rare", 3},
    {"wh3_deer24_fubing_sword", "special", 1},
    {"wh3_deer24_bianjun_1", "special", 2},
    {"longdi_jinjun_deathline", "rare", 3},
    {"wh3_deer24_bianjun_2", "special", 1},
}

local ttc = core:get_static_object("tabletopcaps")
if ttc then
    ttc.add_setup_callback(function()
        ttc.add_unit_list(caps, true)
    end)
end