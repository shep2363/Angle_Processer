import re
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Function to modify .idstv files
def modify_idstv(filepath):
    # Open the file to read its lines
    with open(filepath, 'r') as file:
        lines = file.readlines()

    # Check line 10 for a specific tag and value
    if len(lines) > 10 and "<ProfileType>L</ProfileType>" in lines[9]:
        length_pattern = re.compile(r'<Length>(\d+)</Length>')
        tags_to_modify = ['Filename', 'DrawingIdentification', 'PieceIdentification']

        for index, line in enumerate(lines):
            length_match = length_pattern.search(line)
            # If there's a length value and it's below 279, perform modifications
            if length_match and int(length_match.group(1)) < 279:
                for tag in tags_to_modify:
                    start_tag = f"<{tag}>"
                    end_tag = f"</{tag}>"
                    # If both start and end tags are found, modify the content between them
                    if start_tag in line and end_tag in line:
                        start = line.find(start_tag) + len(start_tag)
                        end = line.find(end_tag)
                        modified_value = line[start:end].replace('0', '')
                        lines[index] = line[:start] + modified_value + line[end:]

        # Write the modified lines back to the file
        with open(filepath, 'w') as file:
            file.writelines(lines)

# Function to modify .nc1 files
def modify_nc1(filepath):
    with open(filepath, 'r') as file:
        lines = file.readlines()

    # Check line 11 for the length value
    if len(lines) > 10:
        try:
            # Attempt to convert the value to a float (decimal number)
            length_value = float(lines[10].strip())
        except ValueError:
            # If conversion fails, skip further modifications for this file
            return
        
        # If the length value is below 279, modify the specified lines
        if length_value < 279:
            for i in [3, 4]:
                lines[i] = lines[i].replace('0', '')

        # Write the modified lines back to the file
        with open(filepath, 'w') as file:
            file.writelines(lines)

# Watchdog's handler for file changes
class FileWatchHandler(FileSystemEventHandler):
    def on_modified(self, event):
        # Ignore directory changes
        if event.is_directory:
            return
        
        # If an .idstv file is modified, run modify_idstv
        if event.src_path.endswith('.idstv'):
            modify_idstv(event.src_path)
        # If an .nc1 file is modified, run modify_nc1
        elif event.src_path.endswith('.nc1'):
            modify_nc1(event.src_path)

def main():
    path_to_watch = "/path_to_directory_to_watch"  # Adjust this to your directory

    print(f"Waiting for 15 seconds before starting...")
    time.sleep(15)  # Introduce a delay of 15 seconds

    # Initialize the event handler and observer from Watchdog
    event_handler = FileWatchHandler()
    observer = Observer()
    observer.schedule(event_handler, path=path_to_watch, recursive=False)
    
    try:
        # Start the Watchdog observer
        observer.start()
        print(f"Watching changes in directory: {path_to_watch}")
        while True:
            # Keep the script running indefinitely to monitor changes
            pass
    except KeyboardInterrupt:
        # Allow stopping the script using Ctrl+C
        observer.stop()
    observer.join()  # Wait for the observer thread to finish

if __name__ == "__main__":
    main()
