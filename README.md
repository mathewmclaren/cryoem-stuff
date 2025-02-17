# cryoem-stuff
A repository for any scripts that could be useful for other people doing cryoEM processing. Some of the code may be poorly written, but it should hopefully do the job!

### bad_frames_finder.sh

Recursively searches a folder and uses the IMOD `header` command to check the number of frames in the movie and compare to a user-specified value. The mismatching movies will be saved to a text file and the bad tilts can be excluded. This was made in a response to an issue with cryoSPARC's reference-based motion correction failing on some micrographs that are missing some frames, as originally documented [here](https://discuss.cryosparc.com/t/reference-based-motion-correction-error-all-movies-must-have-the-same-number-of-frames/12740).

### euler_to_relion.py

A script that will take particle positions in groupings of 2 or 4 from IMOD model files and create a star file with particles aligned along a symmetry defined by the "head" and "tail" of the picks. For two picks, P1 and P2 are head and tail, respectively. For four points, P3 - P2 and P4 - P1 are head and tail - points here must be clockwise starting from the bottom left corner to give the correct head and tail orientation. The centroid (mean between head and tail) is the default particle centre, but the head and tail may be optionally specified. The star file output is generated for Warp by default but can be used to generate Relion 5 star files as well.

Credit to [Daniel Zhang](https://github.com/DanGonite57) for some help with the Euler angles code we originally used for a different script!

### relion_to_clonemodel.py

A script that can take a 3D refinement star file (e.g. run_data.star) and export CSV files for use in generating IMOD clonemodels. A csv file will be generated for each tomogram featured in your star file. 
Further options are available to provide colour, either randomly generated (good for densely-packed particles - see [Figure 1c,d,e here](https://www.nature.com/articles/s41564-023-01469-w/figures/1) for an example). If a classification star file is provided, particles can be coloured by class to show their distribution within tomograms.

This script will hopefully be updated in the near future to be more error-proof and featuresome - mostly as I get better with Python!

### sphere_to_star.py

Takes .mod files generated by IMOD and converts the coordinates and sphere radius values into points on a sphere with Euler angles normal to the surface. The outputted files can then be using for particle extraction in Warp (and potentially Relion).
For the script to work properly, each sphere must be a single point in its own object with a radius defined by the "sphere radius for points" option. The model file names should match the name of the tomogram basename, i.e. Position_001.mod, Position_001_2.mod, otherwise you will need to manually edit the output star file.

Credit to [Daniel Zhang](https://github.com/DanGonite57) for some help with the Euler angles code we originally used for a different script!
### tomo_reorder.sh

An old script to speed up preprocessing of tomographic data collected at the electron bio-imaging centre (eBIC) at Diamond Light Source and the GW4 microscope located at Bristol. The script is rudimentary and makes a lot of assumptions about data collection that were true four years ago when I wrote this. The purpose of the script is to use alignframes to motion correct the movies and apply a gain reference (if provided) then use the newstack command to correctly order the tilts.

The script has long been superseded by other scripts I have written and, more importantly, Warp and Relion 5. It is just here as a reference for work published using it.
