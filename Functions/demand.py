import numpy as np
import xarray as xr
# import Old_Code.attributes_old as attributes_old

# =============================================================================
# Demand modules
# =============================================================================

def LSTRmodel(temp, v):
    """
    calculates energy demand based on fit variables and (population weighted) temperature

    parameters
    ----------
    temp (xarray.DataArray): array with temperature data.
        dimemensions: (country, period, time)
    v (xarray.Set): dataset with dataarrays with variables a-f for with same dimensions as temp
        dimensions: (country, period)

    returns
    -------
    demand (xarray.DataArray)
    """
    G = 1 / (1 + np.exp(-v.e * (temp - v.f)))
    demand = (v.a + v.b * temp) * (1 - G) + (v.c + v.d * temp) * G
    return demand


def compute_demand(ds, ds_fitvalues, varin="temp", varout="demand"):
    """
    computes demand based on temperature.
    Constraints demand by maximum heating/cooling capacity based on historic entsoe demand data

    parameters
    ----------
    ds (xarray.DataSet): array with temperature data.
        dimemensions: (country, period, time)
    ds_fitvalues (xarray.DataSet): dataset with dataarrays with variables a-f and max cooling/heating
        for dimensions as temp. dimensions: (country, period)

    returns
    -------
    ds (xarray.DataSet) with demand array
    """
    ds[varout] = LSTRmodel(ds[varin], ds_fitvalues)
    # bound by highest heating and cooling capacities
    ds[varout] = xr.where(
        (ds[varout] > ds_fitvalues.heating_max) & (ds[varin] < ds_fitvalues.f),
        ds_fitvalues.heating_max,
        ds[varout],
    )
    ds[varout] = xr.where(
        (ds[varout] > ds_fitvalues.cooling_max) & (ds[varin] > ds_fitvalues.f),
        ds_fitvalues.cooling_max,
        ds[varout],
    )
    # ds = attributes_old.set_demand_attributes(ds)
    return ds



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