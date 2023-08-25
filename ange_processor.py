import os
import xml.etree.ElementTree as ET

"""
modifies idstv export from Tekla (Raptor) cutlist export
to reduce the mark length of parts by removing insignificant
digits from part numbers.
"""

def process_idstv_file(filepath):
    """
    Parses through an .IDSTV file at a given path, isolating mark numbers and
    modifying mark numbers by applying transform_id() and writing the modified
    values back to the .IDSTV file.

    DEPENDANCY: xml.etree.ElementTree

    Args:
        string filepath - path containing IDSTV files to be modified

    Returns:
        None - modifies IDSTV files in place
    """
    try:
        tree = ET.parse(filepath)  # Parse the XML file at the given filepath
        root = tree.getroot()  # Get the root element of the XML tree

        # Iterate through all PI elements in the XML
        for pi in root.findall(".//PI"):
            # Find the 'Length' element within the current PI element
            length_element = pi.find("Length")
            if length_element is not None:
                # Cast the text content of 'Length' to a floating-point number
                length = float(length_element.text)
                if length < 279:
                    print(f"Found a Length of {length} which is less than 279 for file {filepath}.")
                    for tag in ['Filename', 'DrawingIdentification', 'PieceIdentification']:
                        # Find the element corresponding to the current tag
                        tag_element = pi.find(tag)
                        if tag_element is not None:
                            # Modify the text content using transform_id()
                            tag_element.text = transform_id(tag_element.text)

        # Write the modified XML back to the file with an XML declaration and UTF-8 encoding
        tree.write(filepath, xml_declaration=True, encoding="UTF-8")
        #print(f"{filepath} has been processed.")  # Not Necessary.

    except (FileNotFoundError, ET.ParseError):
        print(f"Error processing file {filepath}.")

def process_nc1_files(directory):
    """
    Arbitrarily
    Modifies all NC1 files in a given directory by checking the length value
    and if it is less than 279 (milimeters) runs transform_id() on the
    filename and part mark data.

    Args:
        string directory - path containing NC1 files to be modified

    Returns:
        None - modifies NC1 files in place.
    """
    nc1_files = [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith(".nc1")]
    
    for filepath in nc1_files:
        # Read the content of the file to get the length_value
        with open(filepath, 'r') as file:
            lines = file.readlines()
        
        if len(lines) > 10:
            try:
                length_value = float(lines[10].strip())
            except ValueError:
                continue  # Skip the file if the length_value is not a number

            # Modify and rename the file only if the length_value is less than 279
            if length_value < 279:
                for i in [3, 4]:
                    lines[i] = transform_id(lines[i].strip()) + '\n'
                
                with open(filepath, 'w') as file:
                    file.writelines(lines)
                    
                new_filename = transform_id(lines[3].strip())
                new_filepath = os.path.join(directory, new_filename + ".nc1")
                
                if not os.path.exists(new_filepath):  # Check if file already exists
                    os.rename(filepath, new_filepath)
                else:
                    print(f"File {new_filepath} already exists. Skipping renaming.")

def process_nc1_file(filepath):
    """
    Arbitrarily
    Modifies all NC1 files in a given directory by checking the length value
    and if it is less than 279 (milimeters) runs transform_id() on the
    filename and part mark data.

    Args:
        string directory - path containing NC1 files to be modified

    Returns:
        None - modifies NC1 files in place.
    """
    
    # Read the content of the file to get the length_value
    with open(filepath, 'r') as file:
        lines = file.readlines()
    
        if len(lines) > 10:
            try:
                length_value = float(lines[10].strip())
            except ValueError:
                return "ValueError: failed to convert length to float"

            # Modify and rename the file only if the length_value is less than 279
            if length_value < 279:
                for i in [3, 4]:
                    lines[i] = transform_id(lines[i].strip()) + '\n'
                
                with open(filepath, 'w') as file:
                    file.writelines(lines)
                    
                new_filename = transform_id(lines[3].strip())
                new_filepath = os.path.join(filepath, new_filename + ".nc1")
                
                if not os.path.exists(new_filepath):  # Check if file already exists
                    os.rename(filepath, new_filepath)
                else:
                    print(f"File {new_filepath} already exists. Skipping renaming.")

def transform_id(value):
    """
    Given string "value" returns a modified string with non-critical
    0's removed.

    Args:
        string value - value to be modified
    
    Returns:
        string - modified value
    """
    parts = value.split('-')
    # If the provided value does not have three parts (divided by dashes)
    # do not modify that value.
    if len(parts) != 3:
        return value

    # Remove all zeros in the second slice of the given value (Expects: XX###)
    parts[1] = parts[1].replace('0', '')

    # Remove zeros after the last dash and after the first character up to the next character
    first_char = parts[2][0]  # Get the first character
    remaining = parts[2][1:]  # Get the remaining part
    remaining = remaining.lstrip('0')  # Remove leading zeros
    parts[2] = first_char + remaining  # Combine them back

    return '-'.join(parts)

def get_list_of_files(dir, extension):
    """
    Args:
        string extension - file extension to populate file list with
        string dir - directory path to search for files in

    Returns:
        string List - list of all files in given directory with given extension
    """
    return [os.path.join(dir, f) for f in os.listdir(dir) if f.endswith(extension)]


def main():
    directory = input("Please enter the directory containing .idstv and .nc1 files: ")

    idstv_files = get_list_of_files(directory, ".idstv")
    nc1_files = get_list_of_files(directory, ".nc1")

    if not idstv_files:
        print("No .idstv files found in the specified directory.")
        return 1

    for filepath in idstv_files:
        process_idstv_file(filepath)

    if not nc1_files:
        print("No .nc1 files found in the specified directory.")
        return 1

    for filepath in nc1_files:
        process_nc1_file(filepath)

if __name__ == "__main__":
    main()
