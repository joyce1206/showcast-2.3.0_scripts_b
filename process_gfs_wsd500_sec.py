#######################################################################################################
# LICENSE
# Copyright (C) 2021 - INPE - NATIONAL INSTITUTE FOR SPACE RESEARCH - BRAZIL
# This program is free software: you can redistribute it and/or modify it under the terms of the GNU 
# General Public License as published by the Free Software Foundation, either version 3 of the License, 
# or (at your option) any later version.
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without 
# even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General 
# Public License for more details.
# You should have received a copy of the GNU General Public License along with this program. 
# If not, see http://www.gnu.org/licenses/.
#######################################################################################################
__author__ = "Diego Souza"
__copyright__ = "Copyright (C) 2021 - INPE - NATIONAL INSTITUTE FOR SPACE RESEARCH - BRAZIL"
__credits__ = ["Diego Souza", "Regina Ito"]
__license__ = "GPL"
__version__ = "2.3.0"
__maintainer__ = "Diego Souza"
__email__ = "diego.souza@inpe.br"
__status__ = "Production"
#------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------
# Required modules
#--------------------------------
#to run in a pure text terminal:
import matplotlib
#matplotlib.use('Agg')
#--------------------------------
import pygrib                                                # Provides a high-level interface to the ECWMF ECCODES C library for reading GRIB files
from datetime import datetime, timedelta                     # Library to convert julian day to dd-mm-yyyy
from matplotlib.colors import LinearSegmentedColormap        # Linear interpolation for color maps
from mpl_toolkits.axes_grid1.inset_locator import inset_axes # Add a child inset axes to this existing axes.
import matplotlib.colors                                     # Matplotlib colors
import matplotlib.pyplot as plt                              # Plotting library
import numpy as np                                           # Scientific computing with Python
import cartopy, cartopy.crs as ccrs                          # Plot maps
import cartopy.io.shapereader as shpreader                   # Import shapefiles
import time as t                                             # Time access and conversion
import sys                                                   # Import the "system specific parameters and functions" module
import math                                                  # Import math
import os                                                    # Miscellaneous operating system interfaces
from os.path import dirname, abspath                         # Return a normalized absolutized version of the pathname path 
from html_update import update                               # Update the HTML animation 
import warnings                                              # Warning control
warnings.filterwarnings("ignore")
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
# Start the time counter
print('Script started.')
start = t.time()  

# SHOWCast directory:
main_dir = dirname(dirname(abspath(__file__)))

# Choose the visualization extent (min lon, min lat, max lon, max lat)
extent = [float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4]), float(sys.argv[5])]

# Desired resolution
resolution = int(sys.argv[6])

# Define KM_PER_DEGREE
KM_PER_DEGREE = 111.32

# Compute grid dimension
sizex = int(((extent[2] - extent[0]) * KM_PER_DEGREE) / resolution) 
sizey = int(((extent[3] - extent[1]) * KM_PER_DEGREE) / resolution) 

# For logging purposes
path = (sys.argv[1])[:-16]

# Image path
path_gfs = path[:-7]
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------

# Data you want to process
# (to process only the analisys, end and inc should be equal).
hour_ini = 0   # Init time  
hour_end = 24  # End time
hour_inc = 24  # Increment

for hour in range(hour_ini, hour_end, hour_inc):

    path_loop = path_gfs + str(hour).zfill(3)
    print(path_loop)
    
    if (os.path.exists(path_loop)):
    
        print("Processing file: ", path_loop)
        
        # Open the GRIB file
        grib = pygrib.open(path_loop)

        #---------------------------------------------------------------------------------------------
        #---------------------------------------------------------------------------------------------   
        # Read the U component of wind in 500 hPa
        try:
            ucomp = grib.select(name='U component of wind', typeOfLevel = 'isobaricInhPa', level = 500)[0]
        except:
            print("Field not available on the GRIB file. Skipping the current iteration.")
            continue

        # For later use
        init  = ucomp.analDate     # Analysis date / time
        hour  = ucomp.hour         # Run
        ftime = ucomp.forecastTime # Forecast hour
        valid = ucomp.validDate    # Valid date / time 

        #print("GRIB Keys :", sfcps.keys())

        # Read the run time
        run = str(ucomp.hour).zfill(2) + 'Z'
        
        # Read the data for a specific region
        ucomp, lats, lons = ucomp.data(lat1=extent[1],lat2=extent[3],lon1=extent[0]+360,lon2=extent[2]+360)

        # Converting the longitudes to -180 ~ 180
        lons = lons - 360 

        # To smooth the contours
        import scipy.ndimage
        ucomp = scipy.ndimage.zoom(ucomp, 3)
        lats = scipy.ndimage.zoom(lats, 3)
        lons = scipy.ndimage.zoom(lons, 3)

        #print(2mtmp.shape)
        #---------------------------------------------------------------------------------------------
        #---------------------------------------------------------------------------------------------
        # Read the V component of wind in 500 hPa
        try:
            vcomp = grib.select(name='V component of wind', typeOfLevel = 'isobaricInhPa', level = 500)[0]
        except:
            print("Field not available on the GRIB file. Skipping the current iteration.")
            continue
            
        # Read the data for a specific region
        vcomp = vcomp.data(lat1=extent[1],lat2=extent[3],lon1=extent[0]+360,lon2=extent[2]+360)[0]

        # To smooth the contours
        vcomp = scipy.ndimage.zoom(vcomp, 3)
        #---------------------------------------------------------------------------------------------
        #---------------------------------------------------------------------------------------------

        # Calculate the wind speed
        ws = np.sqrt(ucomp**2 + vcomp**2)

        # Calculate the wind direction
        ws_direction = np.arctan2(vcomp,ucomp)

        #---------------------------------------------------------------------------------------------
        #---------------------------------------------------------------------------------------------

        # Create the color scale 
        colors = ["#e7f2f4", "#ceeaee", "#b6e2e8", "#abdcff", "#a4d685", "#9cd04e", "#abcf2a", "#c9d21b", "#e8d50c", "#ffd100", "#ffba00", "#ffa500"]
        cmap = matplotlib.colors.ListedColormap(colors)
        cmap.set_over('#ff8c00')
        cmap.set_under('#fffafa')

        vmin = 0
        vmax = 60
        thick_interval = 5

        #---------------------------------------------------------------------------------------------
        #---------------------------------------------------------------------------------------------
                        
        # Product name
        satellite = "GFS"
        product   = "WSD500_" + run
        
        # Plot configuration
        plot_config = {
        "resolution": resolution, 
        "dpi": 150, 
        "states_color": 'black', "states_width": sizey * 0.00006, 
        "countries_color": 'black', "countries_width": sizey * 0.00012,
        "continents_color": 'black', "continents_width": sizey * 0.00025,
        "grid_color": 'white', "grid_width": sizey * 0.00025, "grid_interval": 5.0,
        "vmin": vmin, "vmax": vmax, "cmap": cmap,
        "title_text": "GFS (0.5°): Wind Speed (kt) & Direction (500 hPa)" + "    -    " + "Init: " + str(init)[:-6] + "Z | Forecast Hour: [" + str(ftime).zfill(3) + "]" + " | Valid: " + str(valid)[:-6] + "Z ", "title_size": int(sizex * 0.005), "title_x_offset": int(sizex * 0.01), "title_y_offset": sizey - int(sizey * 0.016), 
        "thick_interval": thick_interval, "cbar_labelsize": int(sizey * 0.005), "cbar_labelpad": -int(sizey * 0.00),
        "file_name_id_1": satellite,  "file_name_id_2": product
        }
        #---------------------------------------------------------------------------------------------
        #---------------------------------------------------------------------------------------------

        # Choose the plot size (width x height, in inches)
        fig = plt.figure(figsize=(sizex/float(plot_config["dpi"]), sizey/float(plot_config["dpi"])), dpi=plot_config["dpi"])
          
        # Define the projection
        proj = ccrs.PlateCarree()

        # Use the PlateCarree projection in cartopy
        ax = plt.axes([0, 0, 1, 1], projection=proj)
        #ax.set_extent([extent[0], extent[2], extent[1], extent[3]], ccrs.PlateCarree())

        # Define the image extent
        img_extent = [extent[0], extent[2], extent[1], extent[3]]

        # Define de contour interval
        data_min = 0
        data_max = 60 
        interval = 5
        levels = np.arange(data_min,data_max,interval)
         
        # Plot the image
        img1 = ax.contourf(lons, lats, ws, transform=ccrs.PlateCarree(), cmap=cmap, levels=levels, extend='both', zorder=1)
        img2 = ax.contour(lons, lats, ws, transform=ccrs.PlateCarree(), colors='black', linewidths=0.1, levels=levels, zorder=2)
        ax.clabel(img2, inline=1, inline_spacing=0, fontsize=plot_config["cbar_labelsize"],fmt = '%1.0f', colors= 'black', zorder=3)

        # Plot the streamlines
        #qv = plt.quiver(lons, lats, ucomp, vcomp, scale=1300, color='gray', alpha=1.0)
        img3 = ax.streamplot(lons, lats, ucomp, vcomp, density=[1.5, 1.5], linewidth=1, color='gray', zorder=4)

        # Add states and provinces
        shapefile = list(shpreader.Reader(main_dir + '//Shapefiles//ne_10m_admin_1_states_provinces.shp').geometries())
        ax.add_geometries(shapefile, ccrs.PlateCarree(), edgecolor=plot_config["states_color"],facecolor='none', linewidth=plot_config["states_width"], zorder=5)

        # Add countries
        shapefile = list(shpreader.Reader(main_dir + '//Shapefiles//ne_50m_admin_0_countries.shp').geometries())
        ax.add_geometries(shapefile, ccrs.PlateCarree(), edgecolor=plot_config["countries_color"],facecolor='none', linewidth=plot_config["countries_width"], zorder=6)

        # Add continents
        shapefile = list(shpreader.Reader(main_dir + '//Shapefiles//ne_10m_coastline.shp').geometries())
        ax.add_geometries(shapefile, ccrs.PlateCarree(), edgecolor=plot_config["continents_color"],facecolor='none', linewidth=plot_config["continents_width"], zorder=7)
          
        # Add gridlines
        gl = ax.gridlines(color=plot_config["grid_color"], alpha=1.0, linestyle='--', linewidth=0.25, xlocs=np.arange(-180, 180, 5), ylocs=np.arange(-180, 180, 5), draw_labels=False, zorder=8)
        gl.xlabels_top=False
        gl.ylabels_right=False

        # Remove the outline border
        ax.outline_patch.set_visible(False)
          
        # Add a title
        #plt.title("GFS (0.5°): Wind Speed (kt) & Direction (500 hPa)", fontweight='bold', fontsize=7, loc='left')
        #plt.title("Init: " + str(init)[:-6] + "Z | Forecast Hour: [" + str(ftime).zfill(3) + "]" + " | Valid: " + str(valid)[:-6] + "Z ", fontsize=6, loc='right')

        # Add a title
        plt.annotate(plot_config["title_text"], xy=(plot_config["title_x_offset"], plot_config["title_y_offset"]), xycoords='figure pixels', fontsize=plot_config["title_size"], fontweight='bold', color='white', bbox=dict(boxstyle="round",fc=(0.0, 0.0, 0.0), ec=(1., 1., 1.)), zorder=9)
       
        # To put colorbar inside picture
        axins1 = inset_axes(ax, width="2%", height="100%", loc='right', borderpad=0.0)
        
        # Add a colorbar
        ticks = np.arange(plot_config["vmin"], plot_config["vmax"], plot_config["thick_interval"]).tolist()     
        ticks = plot_config["thick_interval"] * np.round(np.true_divide(ticks,plot_config["thick_interval"]))
        ticks = ticks[1:]
        cb = fig.colorbar(img1, cax=axins1, orientation="vertical", ticks=ticks)
        cb.set_label(label='Wind Speed (kt))', size='10', weight='bold') 
        cb.outline.set_visible(False)
        cb.ax.tick_params(width = 0)
        cb.ax.xaxis.set_tick_params(pad=plot_config["cbar_labelpad"])
        cb.ax.yaxis.set_ticks_position('left')
        cb.ax.yaxis.set_label_position('left')
        cb.ax.tick_params(axis='y', colors='black', labelsize=plot_config["cbar_labelsize"])


        #------------------------------------------------------------------------------------------------------
        #------------------------------------------------------------------------------------------------------
        
        # Add labels to specific coordinates

        import configparser
        conf = configparser.ConfigParser()
        if ('.sam.' in path):
            conf.read(main_dir + '//Utils//Labels//labels_gfs_sam.ini')
        else:
            conf.read(main_dir + '//Utils//Labels//labels_gfs_crb.ini')
            
        labels, city_lons, city_lats, x_offsets, y_offsets, sizes, colors, marker_types, marker_colors, marker_sizes = [],[],[],[],[],[],[],[],[],[]

        for each_section in conf.sections():
            for (each_key, each_val) in conf.items(each_section):
                if (each_key == 'label'): labels.append(each_val)
                if (each_key == 'lon'): city_lons.append(float(each_val))
                if (each_key == 'lat'): city_lats.append(float(each_val))
                if (each_key == 'x_offset'): x_offsets.append(float(each_val))
                if (each_key == 'y_offset'): y_offsets.append(float(each_val))
                if (each_key == 'size'): sizes.append(int(each_val))
                if (each_key == 'color'): colors.append(each_val)
                if (each_key == 'marker_type'): marker_types.append(each_val)
                if (each_key == 'marker_color'): marker_colors.append(each_val)
                if (each_key == 'marker_size'): marker_sizes.append(each_val)
         
        import matplotlib.patheffects as PathEffects
        for label, xpt, ypt, x_offset, y_offset, size, col, mtype, mcolor, msize in zip(labels, city_lons, city_lats, x_offsets, y_offsets, sizes, colors, marker_types, marker_colors, marker_sizes):
            ax.plot(xpt, ypt, str(mtype), color=str(mcolor), markersize=int(msize), transform=ccrs.Geodetic(), markeredgewidth=1.0, markeredgecolor=(0, 0, 0, 1), zorder=10)
            txt = ax.text(xpt+x_offset , ypt+y_offset, label, fontsize=int(size), fontweight='bold', color=str(col), transform=ccrs.Geodetic(), zorder=11)
            txt.set_path_effects([PathEffects.withStroke(linewidth=2, foreground='black')])
        
        #------------------------------------------------------------------------------------------------------
        #------------------------------------------------------------------------------------------------------

        # Add logos / images to the plot
        my_logo = plt.imread(main_dir + '//Logos//my_logo.png')
        newax = fig.add_axes([0.01, 0.01, 0.10, 0.10], anchor='SW', zorder=12) #  [left, bottom, width, height]. All quantities are in fractions of figure width and height.
        newax.imshow(my_logo)
        newax.axis('off')

        #------------------------------------------------------------------------------------------------------
        #------------------------------------------------------------------------------------------------------
        
        # Create the satellite output directory if it doesn't exist
        out_dir = main_dir + '//Output//' + satellite
        if not os.path.exists(out_dir):
           os.mkdir(out_dir)

        # Create the product output directory if it doesn't exist
        out_dir = main_dir + '//Output//' + satellite + '//' + product + '//'
        if not os.path.exists(out_dir):
           os.mkdir(out_dir)
   
        #------------------------------------------------------------------------------------------------------
        #------------------------------------------------------------------------------------------------------

        # Save the image
        plt.savefig(out_dir + satellite + '_' + product + '_' + str(init)[:-9].replace('-', '') + str(hour).zfill(2) + 'Z_' + str(ftime).zfill(3) + '.png', bbox_inches='tight', pad_inches=0)

        # Show the image
        #plt.show()
        
        # Update the animation
        nfiles = 30
        update(satellite, product, nfiles)
    
    else:
        
        print("File not available.")

#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
# Put the processed file on the log
import datetime # Basic Date and Time types
import pathlib  # Object-oriented filesystem paths
# Get the file modification time
mtime = datetime.datetime.fromtimestamp(pathlib.Path(path[:-4]).stat().st_mtime).strftime('%Y%m%d%H%M%S')
# Write to the log
with open(main_dir + '//Logs//gnc_log_' + str(datetime.datetime.now())[0:10] + '.txt', 'a') as log:
    log.write(str(datetime.datetime.now()))
    log.write('\n')
    log.write(path + '_c' + mtime + '\n')
    log.write('\n')
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------

# Total processing time
print('Total processing time:', round((t.time() - start),2), 'seconds.') 
