import os
import xml.etree.ElementTree as ET

def modify_nc(filename):
    with open(filename, 'r') as file:
        lines = file.readlines()

    modified = False
    
    if 'BPL' in lines[8]:
        lines[12] = '       5.00\n'
        lines[13] = '       5.00\n'
        lines[14] = '       5.00\n'
        modified = True
    
    # 33 is the index of the 34th line in zero-based indexing
    if len(lines) > 33:
        parts = lines[33].split()
        if parts:  # if parts is not an empty list
            try:
                value = float(parts[-1])  # Convert the last part to float
                parts[-1] = "{:9.2f}".format(-value).rjust(9)  # Change it to negative and format
                lines[33] = ' '.join(parts) + '\n'  # Update the 34th line
                modified = True
            except ValueError as e:
                print(f"Error converting {parts[-1]} to float in file {filename} line 34: {e}")
    
    if modified:
        with open(filename, 'w') as file:
            file.writelines(lines)


def modify_xml(filename):
    tree = ET.parse(filename)
    root = tree.getroot()
    
    for base in root.findall('.//BASE'):
        z_value = float(base.get('Z', '0'))
        if z_value > 128:
            base.set('Z', str(z_value + 5.50))
    
    tree.write(filename)

def process_directory(directory_path):
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            full_path = os.path.join(root, file)
            if file.endswith('.nc'):
                print(f"Modifying: {file}")
                modify_nc(full_path)
            elif file.endswith('.Xml'):
                print(f"Modifying XML: {file}")
                modify_xml(full_path)

directory = input("Please provide the directory path containing the .nc and .xml files: ")
process_directory(directory)
