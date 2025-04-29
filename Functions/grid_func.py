import xarray as xr
import numpy as np
import xesmf as xe

# Preprocess function to apply spatial filter directly at load time
def preprocess(ds, s = 45, n = 60, w = 5, e = 17):
    return ds.sel(lat=slice(s, n), lon=slice(w, e))

# Function to create a reference grid of 1x1 degree over Germany
def create_ref_grid(variable_name):
    # Create reference grid
    lats = np.arange(47, 57)    # Latitude
    lons = np.arange(5, 17)     # Longitude

    # Initialize values for the empty grid (with NaN)
    data = np.full((len(lats), len(lons)), np.nan)

    # Create new xarray.DataArray based on the dimensions
    grid = xr.DataArray(
        data=data,
        coords={"lat": lats, "lon": lons},
        dims=["lat", "lon"],
        name=variable_name
    )
    
    # Add metadata for grid type and CRS
    grid.attrs['gridtype'] = 'lonlat'  # Set gridtype to lonlat (NOT generic)
    grid.attrs['crs'] = 'EPSG:4326'  # CRS for WGS84
    grid['crs'] = 4326
    grid['gridtype'] = 'lonlat'
    
    grid['lat'].attrs['standard_name'] = 'latitude'
    grid['lon'].attrs['standard_name'] = 'longitude'
    return grid

# Function to regrid the dataset to the reference grid
def regrid(ds):
    new_grid = create_ref_grid('new_grid')
    regridder = xe.Regridder(ds, new_grid, 'bilinear')
    ds = regridder(ds)
    return ds