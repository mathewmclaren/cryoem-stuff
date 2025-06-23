import os
import xml.etree.ElementTree as ET
import argparse

def parse_arguments():
	parser = argparse.ArgumentParser(description='A script that converts metadata information from Warp XML files into separated angle, dose and defocus information for pytom-match-pick.')
	parser.add_argument('xml_path', metavar='/path/to/xml', type=str, help='Path to the folder with your files in. [default: current directory]', nargs='?', default='./')
	parser.add_argument('txt_path', metavar='/path/to/output', type=str, help='The location of your output [default: pytom-metadata]', nargs='?', default='pytom-metadata')
	return parser.parse_args()

def extract_position_data(xml_path, txt_path):
    base_name = os.path.splitext(os.path.basename(xml_path))[0]
    tree = ET.parse(xml_path)
    root = tree.getroot()

    angles_text = root.findtext("Angles")
    angles = [line.strip() for line in angles_text.strip().splitlines()]
    with open(f"{txt_path}/{base_name}_angles.tlt", "w") as f:
        f.write("\n".join(angles))

    dose_text = root.findtext("Dose")
    dose = [line.strip() for line in dose_text.strip().splitlines()]
    with open(f"{txt_path}/{base_name}_dose.txt", "w") as f:
        f.write("\n".join(dose))

    grid_ctf = root.find("GridCTF")
    defocus_values = [node.attrib["Value"] for node in grid_ctf.findall("Node")]
    with open(f"{txt_path}/{base_name}_defocus.txt", "w") as f:
        f.write("\n".join(defocus_values))

# Example usage
args = parse_arguments()
xml_path = args.xml_path
txt_path = args.txt_path
os.makedirs(txt_path, exist_ok=True)

for file in os.listdir(xml_path):
	if file.endswith(".xml"): 
		print(f"Processing {file}...")
		extract_position_data(os.path.join(xml_path, file), txt_path)




