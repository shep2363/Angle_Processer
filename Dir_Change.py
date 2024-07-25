import os

def replace_in_file(file_path, old_string, new_string):
    with open(file_path, 'r') as file:
        filedata = file.read()

    filedata = filedata.replace(old_string, new_string)

    with open(file_path, 'w') as file:
        file.write(filedata)

def process_directory(directory):
    old_string = "N:\\Production\\PEDDINGHAUS IDSTV\\W8722\\W8722-260-L\\"
    new_string = "C:\\Users\\fab.automation\\Desktop\\W8722-260-L\\"

    for filename in os.listdir(directory):
        if filename.endswith(".idstv"):  # Modify this if the file extension is different
            file_path = os.path.join(directory, filename)
            replace_in_file(file_path, old_string, new_string)
            print(f"Processed {filename}")

if __name__ == "__main__":
    directory = input("Enter the directory path: ")
    process_directory(directory)
