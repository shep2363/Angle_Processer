import re
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

last_processed = {}

# Function to modify .idstv files
def modify_idstv(filepath):
    with open(filepath, 'r') as file:
        lines = file.readlines()

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
        
        time.sleep(0.1)  # Delay before writing back to the file

        with open(filepath, 'w') as file:
            file.writelines(lines)

# Function to modify .nc1 files
def modify_nc1(filepath):
    with open(filepath, 'r') as file:
        lines = file.readlines()

    if len(lines) > 10:
        try:
            length_value = float(lines[10].strip())
        except ValueError:
            return
        
        if length_value < 279:
            for i in [3, 4]:
                lines[i] = lines[i].replace('0', '')

        time.sleep(0.1)  # Delay before writing back to the file

        with open(filepath, 'w') as file:
            file.writelines(lines)

# Watchdog's handler for file changes
class FileWatchHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.is_directory:
            return

        current_time = time.time()
        if event.src_path in last_processed and current_time - last_processed[event.src_path] < 5:
            return
        
        if event.src_path.endswith('.idstv'):
            modify_idstv(event.src_path)
            print(f"Modified .idstv file: {event.src_path}")
        elif event.src_path.endswith('.nc1'):
            modify_nc1(event.src_path)
            print(f"Modified .nc1 file: {event.src_path}")

        last_processed[event.src_path] = current_time

def main():
    path_to_watch = "C:\\Users\\fab.automation\\Desktop\\Testing angle Processer"

    print(f"Waiting for 15 seconds before starting...")
    time.sleep(15)

    event_handler = FileWatchHandler()
    observer = Observer()
    observer.schedule(event_handler, path=path_to_watch, recursive=False)

    try:
        observer.start()
        print(f"Watching changes in directory: {path_to_watch}")
        while True:
            time.sleep(1)  # Reduce CPU usage by introducing a slight pause in the infinite loop
    except KeyboardInterrupt:
        observer.stop()
    
    observer.join()

if __name__ == "__main__":
    main()
