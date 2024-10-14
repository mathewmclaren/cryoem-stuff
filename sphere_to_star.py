from pathlib import Path
import os
from eulerangles import euler2euler
from scipy.spatial.transform import Rotation
import starfile
import numpy as np
import pandas as pd
import argparse
from imodmodel import ImodModel
# hide the obnoxious warnings and pretend that deprecation isn't going to happen
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
from argparse import RawTextHelpFormatter

# Generates points around spheres defined in IMOD.
# Each sphere must be a single point in its own object with a radius defined by the "sphere radius for points" option
# The script will read the model file and add points every X degrees around each sphere and determine the Euler angles for each point
# Finally, a star file is generated for use in Warp or Relion depending on user preference.
# The model file should match the name of the tomogram basename, i.e. Position_001.mod, Position_001_2.mod, otherwise you will need to manually edit the output star file


parser = argparse.ArgumentParser(
    description="""This script processes a folder with model files and defines spheres around each point.
Each sphere must be a single point in its own IMOD object, and the 'sphere radius for points' value must be set accordingly. 
Model filenames should match the root name of your tomogram, e.g. Position_001.mod, Position_101_2.mod.
When extracting particles, your input pixel size should match the reconstruction pixel size of your tomograms.""",
    formatter_class=RawTextHelpFormatter)
parser.add_argument('path', metavar='/path/to/folder/', type=str,
                    help='Path containing your model files generated in IMOD.')
parser.add_argument('sep', metavar='point_separation', type=int,
                    help='Separation angle between each point in degrees. Smaller values will increase sampling')
parser.add_argument('f_out', metavar='output_star', type=str,
                    help='The output name of your star file.')
parser.add_argument('--relion', action='store_true',
                    help='This setting will output star files for use with Relion 4.0 instead of Warp.')
args = parser.parse_args()

sep_rad = np.radians(args.sep)
column_name = 'rlnMicrographName'
tomostar = '.tomostar'
f_out = args.f_out
if args.relion:
    column_name = 'rlnTomoName'
    tomostar = ''
modpath = Path(args.path)
if not modpath.is_dir():
    raise FileNotFoundError(f"Directory {modpath} does not exist.")
starfile_data = []


def generate_sphere_points(x_centre, y_centre, z_centre, radius, sep_rad):
    points = []
    theta_values = np.arange(0, 2 * np.pi, sep_rad)
    phi_values = np.arange(0, np.pi, sep_rad)

    for theta in theta_values:
        for phi in phi_values:
            x = x_centre + radius * np.sin(phi) * np.cos(theta)
            y = y_centre + radius * np.sin(phi) * np.sin(theta)
            z = z_centre + radius * np.cos(phi)
            points.append([x, y, z])
    return points
    
    
def calculate_euler_angles(points, centre):
    angles = []
    # Define a line vector as the z-axis unit vector (0, 0, 1)
    line_vector = np.array([0, 0, 1])

    for point in points:
        # Define the vector from the centre to the point and normalise
        vector = np.array(point) - np.array(centre)
        vector = vector / np.linalg.norm(vector)
                     
        # Calculate the cross product of the vector and the z-axis unit vector
        cross = np.cross(vector, line_vector)
        if np.linalg.norm(cross) == 0:
            # If the cross product is zero, the vector is aligned with the z-axis
            cross = np.array([1, 0, 0])
        
        # Normalise the cross product
        cross = cross / np.linalg.norm(cross)
        
        # Create the rotation matrix from the cross product and the line vector
        r = Rotation.from_matrix(np.array([cross, -line_vector, vector]).T)
        
        # Extract yaw, pitch, and roll from the rotation matrix
        yaw, pitch, roll = r.as_euler("zyx")
        
        # Convert to ZYZ notation
        eulers = euler2euler(
            (np.degrees(roll), np.degrees(pitch), np.degrees(yaw)),
            source_axes='xyz',
            source_intrinsic=False,
            source_right_handed_rotation=False,
            target_axes='zyz',
            target_intrinsic=True,
            target_right_handed_rotation=True,
            invert_matrix=True)
        angles.append(eulers)
    return angles

for file in modpath.glob("*.mod"):
    try:
        spheres = ImodModel.from_file(file)
        file = file.stem
    except IOError:
        print(f"Error: Could not read the file '{file}'. Skipping this file.")
        continue
    except Exception as e:
        print(f"Error: An unexpected error occurred while processing '{file}': {e}")
        continue
    
    # Loop through each object in the model file to find X/Y/Z coordinates and the sphere radius - 'pdrawsize'
    sphere_array = []
    for obj in spheres.objects:
        pdrawsize = obj.header.pdrawsize
        for contour in obj.contours:
            for point in contour.points:
                sphere_array.append({'pdrawsize': pdrawsize, 'x': point[0], 'y': point[1], 'z': point[2]})

    sphere_data = pd.DataFrame(sphere_array)
    
    for line in range(len(sphere_data)):
        radius = sphere_data.iloc[line]['pdrawsize']
        x, y, z = sphere_data.iloc[line][['x', 'y', 'z']].values

        sphere_points = generate_sphere_points(x, y, z, radius, sep_rad)
        angles = calculate_euler_angles(sphere_points, [x, y, z])

        for point, angle in zip(sphere_points, angles):
            new_row = {
                'rlnCoordinateX': round(point[0]),
                'rlnCoordinateY': round(point[1]),
                'rlnCoordinateZ': round(point[2]),
                'rlnAngleRot': angle[0],
                'rlnAngleTilt': angle[1],
                'rlnAnglePsi': angle[2],
                column_name: file + tomostar
            }
            starfile_data.append(new_row)

star_file = pd.DataFrame(starfile_data)
starfile.write(star_file, f_out)
print(f"Star file written to {f_out}. Processed {len(star_file)} points.")