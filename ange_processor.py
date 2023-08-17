import os
import re
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

modified_files = set()

def safe_file_read(filepath, retries=5, delay=0.2):
    """Safely read a file with retry mechanism."""
    for _ in range(retries):
        try:
            with open(filepath, 'r') as file:
                return file.readlines()
        except Exception as e:
            print(f"Error reading file {filepath}. Retrying... Error: {e}")
            time.sleep(delay)
    print(f"Failed to read {filepath} after multiple attempts.")
    return None

def modify_idstv(filepath):
    lines = safe_file_read(filepath)
    if lines is None:
        return

    content = ''.join(lines)
    if re.search(r'<ProfileType>L</ProfileType>.*?<ProfileCode>L</ProfileCode>', content, re.DOTALL):

        lengths = re.findall(r'<Length>(\d+)</Length>', content)
        if all(int(length) < 279 for length in lengths):

            tags_to_modify = ['Filename', 'DrawingIdentification', 'PieceIdentification']
            for tag in tags_to_modify:
                pattern = re.compile(f"<{tag}>([^<]+)</{tag}>")
                for match in pattern.finditer(content):
                    modified_value = match.group(1).replace('0', '')
                    content = content[:match.start(1)] + modified_value + content[match.end(1):]

            with open(filepath, 'w') as file:
                file.write(content)

def modify_nc1(filepath):
    lines = safe_file_read(filepath)
    if lines is None or len(lines) <= 10:
        return

    try:
        length_value = float(lines[10].strip())
    except ValueError:
        return

    if length_value < 279:
        for i in [3, 4]:
            lines[i] = lines[i].replace('0', '')

        with open(filepath, 'w') as file:
            file.writelines(lines)

class FileWatchHandler(FileSystemEventHandler):

    def on_any_event(self, event):  
        if event.is_directory:
            return

        if event.src_path in modified_files:
            return  # Skip already modified files

        if event.src_path.endswith('.idstv'):
            modify_idstv(event.src_path)
            print(f"Processed .idstv file: {event.src_path}")
            modified_files.add(event.src_path)
        elif event.src_path.endswith('.nc1'):
            modify_nc1(event.src_path)
            print(f"Processed .nc1 file: {event.src_path}")
            modified_files.add(event.src_path)

def main():
    path_to_watch = "//Users//coldensheppard//Desktop//VS Code//Github//Watch_folder"
    print(f"Waiting for 5 seconds before starting...")
    time.sleep(5)

    event_handler = FileWatchHandler()
    observer = Observer()
    observer.schedule(event_handler, path=path_to_watch, recursive=False)

    try:
        observer.start()
        print(f"Watching changes in directory: {path_to_watch}")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    main()
