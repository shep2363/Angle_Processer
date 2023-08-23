import re
import os
import time


def list_files_in_directory(directory, extension):
    """Return a list of filenames with the given extension in the specified directory."""
    with os.scandir(directory) as entries:
        return [entry.path for entry in entries if entry.is_file() and entry.name.endswith(extension)]


def transform_id(value):
    parts = value.split('-')
    if len(parts) != 3:
        return value
    
    parts[1] = parts[1].replace('0', '')
    
    m = re.match(r'(\D)0+', parts[2])
    if m:
        prefix = m.group(1)
        parts[2] = prefix + parts[2][len(prefix):].lstrip('0')

    return '-'.join(parts)

def remove_inner_zeros(match):
    before, main_content, after = match.groups()
    parts = main_content.split('-')
    if len(parts) > 2:
        parts[1] = parts[1].replace('0','')
        main_content = '-'.join(parts)
    return before + main_content + after

def remove_zeros_after_last_dash(match):
    before, upto_last_dash, first_char_after_dash, zeros, remaining, after = match.groups()
    return before + upto_last_dash + first_char_after_dash + remaining + after

def process_idstv_files_in_directory(directory):
    idstv_files = [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith(".idstv")]

    for idstv_file in idstv_files:
        try:
            with open(idstv_file, 'r') as file:
                content = file.read()
                
               
                for tag in ['Filename', 'DrawingIdentification', 'PieceIdentification']:
                    pattern = fr'(<{tag}>)(.*?)(</{tag}>)'
                    content = re.sub(pattern, remove_inner_zeros, content)
                    pattern = fr'(<{tag}>)(.*?-)(.)(0+)([^0].*?)(</{tag}>)'
                    content = re.sub(pattern, remove_zeros_after_last_dash, content)
                    
                    length_pattern = re.compile(r'<Length>(\d+)</Length>')
                    length_match = length_pattern.search(content)
                    
                    if length_match:
                        length = int(length_match.group(1))
                        if length < 279:
                            print(f"Length is less than 279 for file {idstv_file}.")
                            with open(idstv_file, 'w') as file:
                                file.write(content)
                            print(f"{idstv_file} has been processed.")
                        else:
                            print(f"Length is greater than 279 for file {idstv_file}.")
                            print(f"{idstv_file} has not been processed.")
            
        except PermissionError:
            print(f"Waiting for file {idstv_file} to be released")
            time.sleep(1)

def modify_nc1(filepath):
    with open(filepath, 'r') as file:
        lines = file.readlines()
    
    if len(lines) > 10:
        try:
            length_value = float(lines[10].strip())
        except ValueError:
            return 1

        if length_value < 279:
            for i in [3, 4]:
                transformed_line = transform_id(lines[i].strip())
                lines[i] = transformed_line + '\n'
    
    with open(filepath, 'w') as file:
        file.writelines(lines)

def rename_nc1_files(directory):
    nc1_files = [f for f in os.listdir(directory) if f.endswith(".nc1")]
    
    for filename in nc1_files:
        filepath = os.path.join(directory, filename)

        # Read the content of the file to get the length_value
        with open(filepath, 'r') as file:
            lines = file.readlines()
        
        if len(lines) > 10:
            try:
                length_value = float(lines[10].strip())
            except ValueError:
                continue  # Skip the file if the length_value is not a number
            
            # Rename the file only if the length_value is less than 279
            if length_value < 279:
                new_filename = transform_id(filename)
                new_filepath = os.path.join(directory, new_filename)
                
                os.rename(filepath, new_filepath)


def main():
    directory = input("Please enter the directory containing .idstv and .nc1 files: ")

    idstv_files = list_files_in_directory(directory, ".idstv")
    nc1_files = list_files_in_directory(directory, ".nc1")

    if not idstv_files and not nc1_files:
        print("No .idstv or .nc1 files found in the specified directory.")
        return

    # Modify .nc1 files
    for file in nc1_files:
        modify_nc1(file)

    # Process .idstv files and potentially modify .nc1 filenames based on the same logic
    process_idstv_files_in_directory(directory)

    # Rename .nc1 files based on length condition
    rename_nc1_files(directory)

    

if __name__ == "__main__":
    main()
