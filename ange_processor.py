import re

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

    # Check line 11 for the length value
    if len(lines) > 10:
        try:
            length_value = float(lines[10].strip())
        except ValueError:
            # If line 11 doesn't contain a numeric value, skip the modifications
            return
        
        if length_value < 279:
            # Modify lines 4 and 5 to remove zeros
            for i in [3, 4]:  # Lines 4 and 5 have indices 3 and 4
                lines[i] = lines[i].replace('0', '')

        with open(filepath, 'w') as file:
            file.writelines(lines)

def main():
    idstv_files = ["path_to_idstv_file1.idstv", "path_to_idstv_file2.idstv"]  # Add paths to your idstv files here
    nc1_files = ["path_to_nc1_file1.nc1", "path_to_nc1_file2.nc1"]  # Add paths to your nc1 files here

    for file in idstv_files:
        modify_idstv(file)
    
    for file in nc1_files:
        modify_nc1(file)

if __name__ == "__main__":
    main()