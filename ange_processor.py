import re
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

def modify_idstv(filepath):
    with open(filepath, 'r') as file:
        lines = file.readlines()

    if len(lines) > 10 and "<ProfileType>L</ProfileType>" in lines[9]:
        print(f"Modifying .idstv file: {filepath}")

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

    if len(lines) > 10:
        try:
            length_value = float(lines[10].strip())
            print(f"Modifying .nc1 file: {filepath} with length: {length_value}")
            if length_value < 279:
                for i in [3, 4]:
                    lines[i] = lines[i].replace('0', '')
            with open(filepath, 'w') as file:
                file.writelines(lines)
        except ValueError:
            print(f"Skipping .nc1 file {filepath} due to invalid length value")

class FileWatchHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if not event.is_directory:
            if event.src_path.endswith('.idstv'):
                modify_idstv(event.src_path)
            elif event.src_path.endswith('.nc1'):
                modify_nc1(event.src_path)

def main():
    path_to_watch = "C:\\Users\\fab.automation\\Desktop\\Testing angle Processer"
    print(f"Waiting for 15 seconds before starting...")
    time.sleep(15)

    event_handler = FileWatchHandler()
    observer = Observer()
    observer.schedule(event_handler, path=path_to_watch, recursive=False)

    print(f"Watching changes in directory: {path_to_watch}")

    try:
        observer.start()
        while True:
            time.sleep(1)  # This prevents maxing out CPU usage with a tight loop
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    main()
