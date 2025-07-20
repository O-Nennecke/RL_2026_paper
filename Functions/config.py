
# =============================================================================
# settings for solar
# =============================================================================
# solar PV
cT_c1 = 4.3  # constant [dC]
cT_c2 = 0.943  # constant [-]
cT_c3 = 0.028  # constant [dC m2 W-1]
cT_c4 = -1.528  # constant [dC s m-1]
gamma = -0.005  # constant [--]
temp_ref = 25  # reference temperature [dC]

gstc = 1000  # standard test conditions [W m-2]
shift_doy = 186  # if HadGEM : 180
pv_constants = [cT_c1, cT_c2, cT_c3, cT_c4]

# =============================================================================
# settings for wind
# =============================================================================

height_ref = 100.0  # height of available wind data [m]
height_ref_ERA5 = 100.0  # height of available wind data ERA5 [m]
time_oper = 24  # operational time of hub [h/day]

v_cutin0 = 3.5  # cut-in wind speed [m/s]
v_rated0 = 13   # rated wind speed [m/s]
v_cutout0 = 25  # cut_out wind speed [m/s]

a_onshore = 1/7 #0.143  # onshore roughness energy_type [-]
a_offshore = 0.11  # offshore roughness energy_type [-]

# v_cutinland = 2
# v_ratedland = 10
# v_cutoutland = 25

# v_cutinoff = 3
# v_ratedoff = 15
# v_cutoutoff = 27

# height_onshore = 90.0  # height onshore wind turbines [m]
# height_offshore = 110.0  # height offshore wind turbines [m]