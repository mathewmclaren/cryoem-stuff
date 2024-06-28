#!/bin/bash

##### WARNING #####
# This script is very deprecated and was made for very specific datasets collected at Bristol and Diamond Light Source (eBIC) in very specific ways!
# Everything relies on tilt series having 41 or 61 images in collection methods that were specific to how we operated in 2019-2021
# The code simply navigates into each folder and:
# - runs the IMOD alignframes command with a gain reference (if specified) to generate an aligned (but misordered) tilt stack
# - runs newstack with the -secs argument to manually reorder all the frames into the correct order, based on collection conditions
# Once complete, the user can then use Etomo, Aretomo or similar to run tomogram reconstruction.

# A second, slightly more robust, script eventually replaced this which was again superseded by using Warp instead for motion correction and tilt series generation
# The rest of the code is as-is, but with some extra comments for clarity and some better formatting
###################


# This script will ask the user for the file format for the images the tomogram was collected in and the number of fractions in each image.
# If there is a gain reference the path can be entered. 
# The script will then run through all the folders in the directory it was executed in and create an mrc file for each tomogram.

# The most fiddly bit is the tilt collection scheme, which is also very important to get right! There are 3 options:
# 1) Bristol (old) - this is for all data collected pre-2020ish, where the tilt collection runs from -20 to 60 and -22 to -60. This has been superseded by dose-symmetric tilt collection.
# 2) eBIC (SerialEM) - this is for eBIC data collected using the SerialEM software. This runs in dose-symmetric fashion (e.g. 0, 2, 4, 6, 8, 10, -2, 4, -6, -8, -10, 12, etc.) and as far as I know is relevant for all SerialEM data collection here.
# 3) Bristol and eBIC using Tomo - This is for Bristol data post-2020ish and for any eBIC data collected using Tomo instead of SerialEM. The dose-symmetric collection is different (0, 2, -2, -4, 4, 6, etc.) but should be consistent for most future data collections.

# If you are unsure about this, you are best checking the individual tilts themselves. You can look at the naming system of Tomo data and it will be named something like Position_1_001[0.00]_fractions.tiff where 001 is the order the frames are collected in and [0.00] is the tilt. Look through in order and see how the tilts given match up to the options above.



printf "Please enter the file format used for the tomograms:\ntif \ntiff \nmrc \ndm4 \n\n"
read format
printf "Please enter the number of fractions in each image.\nIf you are unsure, use the header command (e.g header image.tif) and the number of sections equals the number of fractions\n\n"
read frac
printf "If there is a gain reference file, please enter the path and filename. You can tab complete to navigate to the directory\nPlease enter 0 if the gain reference is already applied\n\n"
read -e gain
printf "Where did you collect you data? Type the number corresponding to where you collected data.\nBristol (old): 1\neBic (SerialEM): 2\nBristol and eBIC (dose-symmetric) using Tomo: 3\n\n"
read -e tem
printf "How many tilts were collected? \n41\n61\n\n 61 is fairly standard, 41 is used occasionally at both Bristol and eBIC.The script will not work with any other input right now.\n\n"
read -e number
printf "Add any additional arguments here for the newstack command, e.g. if you have super-resolution data and want to apply fourier cropping then add -ftreduce 2\n\n"
read -e args
cwd=$(pwd)
for i in */; do
	cd $i
	printf "Entering directory $i\n\n"
	num=$(find . -maxdepth 1 -name "*.$format" | wc -l)
	# sanity check to ensure that folders with incomplete tilt series are ignored
	if (($num > 40)); then
		tomo=$(basename "$PWD")
		if [ $gain == 0 ]; then
			alignframes -br $frac *.$format "$tomo"_align.mrc
		else
			alignframes -gain "$gain" -br $frac *.$format "$tomo"_align.mrc
		fi

		if [ $tem == 1 ]; then
			if [ $number == 61 ]; then
				newstack "$tomo"_align.mrc $args -secs 40,39,38,37,36,35,34,33,32,31,30,29,28,27,26,25,24,23,22,21,20,19,18,17,16,15,14,13,12,11,10,9,8,7,6,5,4,3,2,1,0,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60 "$tomo"_reordered.mrc
				rm "$tomo"_align.mrc
			elif [ $number == 41 ]; then
					newstack "$tomo"_align.mrc $args -secs 27,26,25,24,23,22,21,20,19,18,17,16,15,14,13,12,11,10,9,8,7,6,5,4,3,2,1,0,28,29,30,31,32,33,34,35,36,37,38,39,40 "$tomo".mrc
					rm "$tomo"_align.mrc
			else
				printf "The script will only work for 41 or 61 tilt steps!\nExiting.."
				exit
			fi

		elif [ $tem == 2 ]; then
			if [ $number == 61 ]; then
					newstack "$tomo"_align.mrc $args -secs 60,59,58,57,56,50,49,48,47,46,40,39,38,37,36,30,29,28,27,26,20,19,18,17,16,10,9,8,7,6,0,1,2,3,4,5,11,12,13,14,15,21,22,23,24,25,31,32,33,34,35,41,42,43,44,45,51,52,53,54,55 "$tomo"_reordered.mrc
					rm "$tomo"_align.mrc
			elif [ $number == 41 ]; then
					newstack "$tomo"_align.mrc $args -secs 40,39,36,35,34,30,29,28,24,23,22,18,17,16,12,11,10,6,5,4,0,1,2,3,7,8,9,13,14,15,19,20,21,25,26,27,31,32,33,37,38 "$tomo".mrc
					rm "$tomo"_align.mrc
			else
				printf "The script will only work for 41 or 61 tilt steps!\nExiting.."
				exit
			fi

		elif [ $tem == 3 ]; then

			if [ $number == 61 ]; then
				newstack "$tomo"_align.mrc $args -secs 59,58,55,54,51,50,47,46,43,42,39,38,35,34,31,30,27,26,23,22,19,18,15,14,11,10,7,6,3,2,0,1,4,5,8,9,12,13,16,17,20,21,24,25,28,29,32,33,36,37,40,41,44,45,48,49,52,53,56,57,60 "$tomo".mrc
				rm "$tomo"_align.mrc
			elif [ $number == 41 ]; then
				newstack "$tomo"_align.mrc $args -secs 39,38,35,34,31,30,27,26,23,22,19,18,15,14,11,10,7,6,3,2,0,1,4,5,8,9,12,13,16,17,20,21,24,25,28,29,32,33,36,37,40 "$tomo".mrc
				rm "$tomo"_align.mrc
			else
				printf "The script will only work for 41 or 61 tilt steps!\nExiting.."
				exit
			fi
		else
				printf "You must type ebic or bristol to choose the data collection conditions!\nExiting.."
				exit
		fi

	else
		printf "This folder does not contain tomogram data or contains too few tilts, ignoring folder!\n\n"
	fi
	printf "Leaving directory $i\n\n"
	cd $cwd
done
