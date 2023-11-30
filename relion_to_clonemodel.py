import os, glob, starfile, sys
import numpy as np
from eulerangles import euler2euler
from pathlib import Path 
import pandas as pd
import argparse
from scipy.spatial.transform import Rotation as R

parser = argparse.ArgumentParser(description='A script to take a star file input with aligned particles export csv files for use in generating IMOD clonemodels. A csv file will be generated for each tomogram featured in your star file.')
parser.add_argument('input_star', metavar='/path/to/file.star', type=str,
                    help='The path to star file you wish to use. This should be a Relion 3.1 star file, i.e. it has the optics group section at the top.')

parser.add_argument('tomo_px', metavar='tomo_pixelsize', type=str,
                    help='The pixel size of the tomograms you wish to apply your particles to. You can check this using the header command on your tomogram.')
parser.add_argument('--nocolour', action='store_true',
                    help='Set this to disable random colouring of each.')
parser.add_argument('--class_colour', action='store_true',
                    help='Set this to colour based on the class your particles are grouped into - requires a 3D classification star file.')
parser.add_argument('--force_pixel_size', metavar='forced_pixelsize',
                    help='Use this option to force a specific pixel size from your data (not your tomogram). If your star file has an incorrect pixel size, specify the correct value with this option.')
args = parser.parse_args()

input_star = sys.argv[1]
tomo_px = float(sys.argv[2])
# read star and exclude the optics group
full_star = starfile.read(input_star)
# fix for Relion 3 star files
if "optics" in full_star:
	particles = full_star["particles"]
	optics = full_star["optics"]
	pixelsize = optics['rlnImagePixelSize'].iloc[0]
	px_rescale = tomo_px / pixelsize
else:
	particles = full_star
	if "rlnPixelSize" in particles:
		pixelsize = particles['rlnPixelSize'].iloc[0]
	else:
		pixelsize = tomo_px
	px_rescale = tomo_px / pixelsize
if args.force_pixel_size is not None:
	forced_pixelsize = float(args.force_pixel_size)
	px_rescale = tomo_px / forced_pixelsize
	print(f"Forcing the pixel size of your data to be {forced_pixelsize} Apx, you should probably only be doing this if you know your star file pixel size is wrong!")

# get number of tomograms and tomogram list
tomos = particles.drop_duplicates('rlnMicrographName')
tomos = tomos.reset_index(drop=True)
tomo_count = len(tomos['rlnMicrographName'])

# fix for star files that haven't been through Relion yet
if 'rlnOriginZAngst' in particles.columns:
	particles['rlnCoordinateX'] = (particles['rlnCoordinateX'] * pixelsize - particles['rlnOriginXAngst'] ) / tomo_px
	particles['rlnCoordinateY'] = (particles['rlnCoordinateY'] * pixelsize - particles['rlnOriginYAngst']) / tomo_px
	particles['rlnCoordinateZ'] = (particles['rlnCoordinateZ'] * pixelsize - particles['rlnOriginZAngst']) / tomo_px
else: 
	particles['rlnCoordinateX'] = ( particles['rlnCoordinateX'] * pixelsize) / tomo_px
	particles['rlnCoordinateY'] = ( particles['rlnCoordinateY'] * pixelsize) / tomo_px
	particles['rlnCoordinateZ'] = ( particles['rlnCoordinateZ'] * pixelsize) / tomo_px


i = 0
while i < tomo_count:


	# get tomogram name and number of particles
	tomo_name = tomos.at[i, 'rlnMicrographName']
	tomo_stripped = os.path.splitext(tomo_name)[0]
	lines = particles.loc[particles['rlnMicrographName'] == tomo_name]
	lines = lines.reset_index(drop=True)

	# generate blank dataframe
	coords = pd.DataFrame(index=range(len(lines)),columns=[])
	# this needs to be the contour number, Optics Group should probably return as 1
	coords[0] = 1
	coords[1] = lines['rlnCoordinateX']
	coords[2] = lines['rlnCoordinateY']
	coords[3] = lines['rlnCoordinateZ']
	coords[4] = lines['rlnAngleRot']
	coords[5] = lines['rlnAngleTilt']
	coords[6] = lines['rlnAnglePsi']
	# this gives some colouring just for fun - will replace with RNG in the future
	#	if arg.nocolour is false:
	if args.class_colour is True:
		coords[7] = lines['rlnClassNumber']
	elif args.nocolour is True:
		coords[7] = 1
	else:
		coords[7] = np.random.randint(0,255,size=len(coords))

	eulers = coords[[4,5,6]].to_numpy()
	ori = R.from_euler("zyz", -eulers, degrees=True)
	coords[[4,5,6]] = ori.as_euler("XYZ", degrees=True)

	print('Saving ' + tomo_stripped + '_clonemodel.csv...')
	np.savetxt(tomo_stripped + '_clonemodel.csv', coords, delimiter=",", fmt='%1g')
	i += 1

