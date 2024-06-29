# cryoem-stuff
A repository for any scripts that could be useful for other people doing cryoEM processing. Some of the code may be poorly written, but it should hopefully do the job!

### bad_frames_finder.sh

Recursively searches a folder and uses the IMOD `header` command to check the number of frames in the movie and compare to a user-specified value. The mismatching movies will be saved to a text file and the bad tilts can be excluded. This was made in a response to an issue with cryoSPARC's reference-based motion correction failing on some micrographs that are missing some frames, as originally documented [here](https://discuss.cryosparc.com/t/reference-based-motion-correction-error-all-movies-must-have-the-same-number-of-frames/12740).

### relion_to_clonemodel.py

A script that can take a 3D refinement star file (e.g. run_data.star) and export CSV files for use in generating IMOD clonemodels. A csv file will be generated for each tomogram featured in your star file. 
Further options are available to provide colour, either randomly generated (good for densely-packed particles - see [Figure 1c,d,e here](https://www.nature.com/articles/s41564-023-01469-w/figures/1) for an example). If a classification star file is provided, particles can be coloured by class to show their distribution within tomograms.

This script will hopefully be updated in the near future to be more error-proof and featuresome - mostly as I get better with Python!

### tomo_reorder.sh

An old script to speed up preprocessing of tomographic data collected at the electron bio-imaging centre (eBIC) at Diamond Light Source and the GW4 microscope located at Bristol. The script is rudimentary and makes a lot of assumptions about data collection that were true four years ago when I wrote this. The purpose of the script is to use alignframes to motion correct the movies and apply a gain reference (if provided) then use the newstack command to correctly order the tilts.

The script has long been superseded by other scripts I have written and, more importantly, Warp and Relion 5. It is just here as a reference for work published using it.