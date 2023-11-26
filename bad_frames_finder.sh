#!/bin/bash

# change me to run more parallel processes!
procs=16
display_help() {
	echo "Usage: $0 <file_path> <frame_count> <extension>"
	echo "       $0 -h|--help"
	echo ""
	echo "Your input path should be the path to your micrographs. If they are within subfolders, e.g. GridSquare_XXXX then run it in the folder containing these as it will scan recursively."
	echo "The frame count should be your expected number of fractions and your file extension will likely be mrc, tif or tiff."
	echo "Options:"
	echo "  -h, --help   Display this help message and exit."
	echo ""
}

if [ "$1" == "-h" ] || [ "$1" == "--help" ]; then
	display_help
	exit 0
fi

if [ $# -ne 3 ]; then
    read -e -p "Enter the path of your movies - the script will search recursively so they do not all need to be in the root directory: " dir
    read -p "Enter the expected frame count of your movies: " frame_count
    read -p "Enter the file extension of your movies: " ext
else
    dir=$1
    frame_count=$2
    ext=$3
fi

frames_check() {
    file="$1"
    frames=$(header "$file" | grep sections | awk '{print $NF}')
    echo "Checking file ${file}..."
    if [ "$frames" != "$2" ]; then
        echo "File: $file - Frames: $frames" >> bad_movies.txt
        echo "Frames: $frames"
    fi
}

export -f frames_check

find "$dir" -name "*${ext}" -print | parallel -j $procs frames_check {} $frame_count
