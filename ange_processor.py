import re
import os
import time


def transform_id(value):
    parts = value.split('-')
    if len(parts) != 3:
        return value  # Return original value if it doesn't match the format

    # Handle each part
    # For the first part, don't modify
    # For the second part, remove all zeros
    parts[1] = parts[1].replace('0', '')
    # For the third part, remove zeros following the first character and up to any non-zero character
    m = re.match(r'(\D)0+', parts[2])
    if m:
        prefix = m.group(1)  # Capture the non-digit character
        parts[2] = prefix + parts[2][len(prefix):].lstrip('0')

    return '-'.join(parts)

# Updated code based on the provided script

def process_idstv_files_in_directory_updated(directory):
    
    idstv_files = [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith(".idstv")]

    for idstv_file in idstv_files:
        
        try:
            with open(idstv_file, 'r') as file:
                content = file.read()

            # Process the specific tags
            for tag in ['Filename', 'DrawingIdentification', 'PieceIdentification']:
                if len(content) > 9 and "<ProfileType>L</ProfileType>" in content[9]:
                    
                
                    length_pattern = re.compile(r'<Length>(\d+)</Length>')
                    length_match = length_pattern.search(content)
                    if length_match:
                        length = int(length_match.group(1))
                        if length < 279:
                            

                
                
                # Remove zeros between the first and last dashes
                            def remove_inner_zeros(match):
                                before, main_content, after = match.groups()
                                
                                # Split by dash, process inner parts and rejoin
                                parts = main_content.split('-')
                                if len(parts) > 2:
                                    parts[1] = parts[1].replace('0','')
                                    main_content = '-'.join(parts)
                                return before + main_content + after
                            
                            pattern = fr'(<{tag}>)(.*?)(</{tag}>)'
                            content = re.sub(pattern, remove_inner_zeros, content)

                            # After the last dash and the first character following it, remove zeros up to the first character
                            def remove_zeros_after_last_dash(match):
                                before, upto_last_dash, first_char_after_dash, zeros, remaining, after = match.groups()
                                return before + upto_last_dash + first_char_after_dash + remaining + after
                            
                            pattern = fr'(<{tag}>)(.*?-)(.)(0+)([^0].*?)(</{tag}>)'
                            content = re.sub(pattern, remove_zeros_after_last_dash, content)

                        with open(idstv_file, 'w') as file:
                            file.write(content)
                            rename_nc1_files(directory) 


                         
        except PermissionError:
            print(f"Waiting for file {idstv_file} to be released")
            time.sleep(1)


def main_updated():
    directory = input("Please enter the directory containing .idstv and .nc1 files: ")
    idstv_files = list_files_in_directory(directory, ".idstv")
    nc1_files = list_files_in_directory(directory, ".nc1")

    if not idstv_files and not nc1_files:
        print("No .idstv or .nc1 files found in the specified directory.")
        return

    process_idstv_files_in_directory_updated(directory)
    
    for file in nc1_files:
        modify_nc1(file)


def modify_nc1(filepath):
    with open(filepath, 'r') as file:
        lines = file.readlines()

    # Ensure there are more than 10 lines in the file
    if len(lines) > 10:
        try:
            # Extract the length value from line 11
            length_value = float(lines[10].strip())
        except ValueError:
            # If line 11 doesn't contain a numeric value, exit the function
            return 1

        # Check if the length_value is less than 279
        if length_value < 279:
            # Check and modify lines 4 and 5
            for i in [3, 4]:  # Lines 4 and 5 have indices 3 and 4
                transformed_line = transform_id(lines[i].strip())  # Transform the entire line
                lines[i] = transformed_line + '\n'  # Add newline character back to the modified line

    # Write back the modified content
    with open(filepath, 'w') as file:
        file.writelines(lines)

def rename_nc1_files(directory):
    """
    Renames .nc1 files in the given directory based on the logic to remove zeros.
    """
    nc1_files = [f for f in os.listdir(directory) if f.endswith(".nc1")]
    
    for filename in nc1_files:
        new_filename = transform_id(filename)  # Using your existing transform_id function
        old_filepath = os.path.join(directory, filename)
        new_filepath = os.path.join(directory, new_filename)
        
        # Rename the file
        os.rename(old_filepath, new_filepath)


def list_files_in_directory(directory, extension):
    """Return a list of filenames with the given extension in the specified directory."""
    with os.scandir(directory) as entries:
        return [entry.path for entry in entries if entry.is_file() and entry.name.endswith(extension)]

def main():
    directory = input("Please enter the directory containing .idstv and .nc1 files: ")

    idstv_files = list_files_in_directory(directory, ".idstv")
    nc1_files = list_files_in_directory(directory, ".nc1")

    if not idstv_files and not nc1_files:
        print("No .idstv or .nc1 files found in the specified directory.")
        return
    for file in nc1_files:
        modify_nc1(file)

    for file in idstv_files:
        process_idstv_files_in_directory_updated(directory)
    
    

    
if __name__ == "__main__":
    main()
