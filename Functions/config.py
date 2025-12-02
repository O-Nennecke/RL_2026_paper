
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



# =============================================================================
# Parts of this code are adapted from: 
# Van der Most, L., Van der Wiel, K., Benders, R. M. J., Gerbens-Leenes, P. W., Kerkmans, P., & Bintanja, R. (2022). 
# Extreme events in the European renewable power system: Validation of a modeling framework to estimate renewable electricity 
# production and demand from meteorological data. Renewable and Sustainable Energy Reviews, 170(112987). https://doi.org/10.1016/j.rser.2022.112987


# MIT License

# Copyright (c) 2022 Lieke van der Most

# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), 
# to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, 
# and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, 
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
# =============================================================================