# Pierce Transit Work Order Visualization

# Create shapefile of open work orders for bus stop locations.
# Save the created shapefile in Bus Stop geodatabase for future analysis.

import arcpy
import pandas as pd
import re
import os

# Overview of steps:
# 	1. Open work order csv file and edit for compatability.
#	2. Merge bus stop (bs) locations to work orders (wo).
#	3. Go from CSV to shapefile or webmap for use.


try:
	arcpy.env.workspace = r"D://PT/BusStops"
	arcpy.env.overwriteOutput = True

	# Step 1: Organize work order csv file for use.
	print "Initializing data organization."
	work = pd.read_csv('workorders.csv')
	work.columns = work.columns.str.replace(' ', "_")
	work = work.rename(columns = {
		'Equipment_ID': 'BS_NUM',
		'Date_and_time_opened': 'DATE_OPEN',
		'Work_order_number': 'WORK_NUM'})
	work = work[['BS_NUM', 'DATE_OPEN', 'WORK_NUM']]

	# Edit field to remove non-number elements.
	work['BS_NUM'] = work['BS_NUM'].str.replace(r'\D+', '')

	# Prepare bus stop csv file for join.
	bs = pd.read_csv('busstops.csv')
	bs.drop(bs.columns[[0, 5]], axis=1, inplace=True)
	bs = bs.rename(columns={
		'bs_sname': 'BS_NUM',
		'bs_lname': 'BS_NAME'})

	# Step 2: Join two csv files and create shapefile.
	# Edit field to ensure merge ability (BS_NUM as 'object').
	bs['BS_NUM'] = bs['BS_NUM'].apply(lambda x: str(x))

	# Join two csv files on Bus Stop Number as index.
	print "Merging data into one CSV."
	bs_work = pd.merge(work, bs, on='BS_NUM', how='inner')
	bs_work.to_csv('BS_WO.csv')

	# Step 3: Display the points in a map.
	# Set variables.
	in_table = "BS_WO.csv"
	x_coords = "longitude"
	y_coords = "latitude"
	out_layer = "bs_wo_pts"
	saved_layer = "bs_wo_pts.lyr"
	spatialref = arcpy.SpatialReference(4326)

	# Make the XY Event Layer and save as .lyr.
	print "Creating shapefile."
	arcpy.management.MakeXYEventLayer(in_table, x_coords, y_coords, out_layer, spatialref)
	arcpy.management.SaveToLayerFile(out_layer, saved_layer)

	# Create shapefile with date in name.
	now = datetime.datetime.now()
	mdy = now.strftime("%m%d%Y")
	out_name = "bs_wo_" + mdy + ".shp"
	arcpy.management.CopyFeatures(saved_layer, out_name)

	# Copy shapefile to geodatabase.
	print "Copying shapefile to geodatabase."
	in_features = out_name
	out_gdb = "BusStops.gdb"
	arcpy.conversion.FeatureClassToGeodatabase(in_features, out_gdb)

	print "\nComplete. Bus stop work orders compiled."

# Catch errors.
except:
	print(arcpy.GetMessages())
