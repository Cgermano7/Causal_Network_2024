#Within Schooner, reformatted files so that the 4x daily values were averaged within the month.

import os
import numpy as np
from netCDF4 import Dataset

def process_nc_file(input_filepath, output_filepath):
    # Open the input NetCDF file
    with Dataset(input_filepath, 'r') as src:
        # Read dimensions
        time = src.variables['time']
        latitude = src.variables['latitude'][:]
        longitude = src.variables['longitude'][:]
        
        # Read the total precipitation data
        tp = src.variables['tp'][:]
        
        # Reshape the data to (days, 4, latitude, longitude)
        days = tp.shape[0] // 4
        tp_daily = tp[:days*4].reshape(days, 4, latitude.shape[0], longitude.shape[0]).mean(axis=1)
        
        # Create a new NetCDF file to store the daily data
        with Dataset(output_filepath, 'w') as dst:
            # Create dimensions
            dst.createDimension('time', days)
            dst.createDimension('latitude', len(latitude))
            dst.createDimension('longitude', len(longitude))
            
            # Create variables
            time_var = dst.createVariable('time', 'i4', ('time',))
            latitude_var = dst.createVariable('latitude', 'f4', ('latitude',))
            longitude_var = dst.createVariable('longitude', 'f4', ('longitude',))
            tp_var = dst.createVariable('tp', 'f4', ('time', 'latitude', 'longitude'))
            
            # Assign attributes
            time_var.units = time.units
            time_var.calendar = time.calendar
            latitude_var[:] = latitude
            latitude_var.units = src.variables['latitude'].units
            longitude_var[:] = longitude
            longitude_var.units = src.variables['longitude'].units
            tp_var.units = src.variables['tp'].units
            tp_var.long_name = src.variables['tp'].long_name
            
            # Write data to the new variables
            time_var[:] = np.arange(days)  # Simple range for days
            tp_var[:] = tp_daily

def main(input_dir, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for filename in os.listdir(input_dir):
        if filename.endswith('.nc'):
            input_filepath = os.path.join(input_dir, filename)
            output_filepath = os.path.join(output_dir, 'daily_' + filename)
            process_nc_file(input_filepath, output_filepath)
            print("Processed {} and saved to {}".format(filename, output_filepath))

if __name__ == "__main__":
    input_dir = "/ourdisk/hpc/ai2es/datasets/dont_archive/era5/TP"
    output_dir = "/ourdisk/hpc/ai2es/datasets/dont_archive/era5/TP_Daily"
    main(input_dir, output_dir)
