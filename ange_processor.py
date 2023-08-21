import re
import os

def modify_idstv(filepath):
    with open(filepath, 'r') as file:
        lines = file.readlines()

    # Check line 10 for the presence of <ProfileType>L</ProfileType>
    if len(lines) > 10 and "<ProfileType>L</ProfileType>" in lines[9]:
        length_pattern = re.compile(r'<Length>(\d+)</Length>')
        tags_to_modify = ['Filename', 'DrawingIdentification', 'PieceIdentification']

        for index, line in enumerate(lines):
            length_match = length_pattern.search(line)
            if length_match and int(length_match.group(1)) < 279:
                for tag in tags_to_modify:
                    start_tag = f"<{tag}>"
                    end_tag = f"</{tag}>"
                    if start_tag in line and end_tag in line:
                        start = line.find(start_tag) + len(start_tag)
                        end = line.find(end_tag)
                        modified_value = line[start:end].replace('0', '')
                        lines[index] = line[:start] + modified_value + line[end:]

        with open(filepath, 'w') as file:
            file.writelines(lines)

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
            # Check if lines 4 and 5 have a zero between the third last and last characters
            for i in [3, 4]:  # Lines 4 and 5 have indices 3 and 4
                if lines[i][-2] == '0':  # Check the second-last character for zero
                    # Modify lines 4 and 5 to remove zeros from the first 14 characters
                    lines[i] = lines[i][:14].replace('0', '') + lines[i][14:]

    # Write back the modified content
    with open(filepath, 'w') as file:
        file.writelines(lines)


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

    for file in idstv_files:
        modify_idstv(file)
    
    for file in nc1_files:
        modify_nc1(file)

if __name__ == "__main__":
    main()
