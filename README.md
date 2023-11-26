# cryoem-stuff
A repository for any scripts that could be useful for other people doing cryoEM processing. Some of the code may be poorly written, but it shiuld hopefully do the job!

### bad_frames_finder.sh

Recursively searches a folder and uses the IMOD `header` command to check the number of frames in the movie and compare to a user-specified value. The mismatching movies will be saved to a text file and the bad tilts can be excluded. This was made in a response to an issue with cryoSPARC's reference-based motion correction failing on some micrographs that are missing some frames, as originally documented [here](https://discuss.cryosparc.com/t/reference-based-motion-correction-error-all-movies-must-have-the-same-number-of-frames/12740).
