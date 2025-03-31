import numpy as np
import cftime
from datetime import datetime

def add_winter_calendar(ds):
    # Get the time coordinate
    time = ds['time']
    
    # Function to calculate day of winter and year
    def calculate_winter_date(t):
        if isinstance(t, (np.datetime64, datetime)):
            # Handle numpy datetime64 and datetime objects
            date = np.datetime64(t, 'D')
            year = date.astype('datetime64[Y]').astype(int) + 1970
            month = date.astype('datetime64[M]').astype(int) % 12 + 1
            day = int(date.astype('datetime64[D]').astype(int) % 31 + 1)
        elif isinstance(t, (cftime.DatetimeNoLeap, cftime.Datetime360Day)):
            # Handle cftime objects directly
            year, month, day = t.year, t.month, t.day
        else:
            raise TypeError(f"Unsupported time type: {type(t)}")
        
        # Determine winter year (assign to the year of October)
        winter_year = year if month >= 10 else year - 1
        
        # Start date of winter season (Oct 1st)
        if isinstance(t, (np.datetime64, datetime)):
            winter_start = np.datetime64(f"{winter_year}-10-01", 'D')
            day_of_winter = (date - winter_start).astype(int) + 1
        else:
            winter_start = type(t)(winter_year, 10, 1)
            day_of_winter = (t - winter_start).days + 1
        
        return winter_year, day_of_winter
    
    # Apply function to all time points
    winter_years, day_of_winter = zip(*[calculate_winter_date(t) for t in time.values])

    # Convert the results to numpy arrays
    winter_years = np.array(winter_years)
    day_of_winter = np.array(day_of_winter)

    # Add coordinates to the dataset
    ds = ds.assign_coords(
        winter_year=('time', winter_years),
        day_of_winter=('time', day_of_winter),
        winter_season=('time', [f"{y}-{d:03d}" for y, d in zip(winter_years, day_of_winter)])
    )

    return ds
