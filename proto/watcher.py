import sys
import time
import subprocess
from loguru import logger
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent


class EventHandler(FileSystemEventHandler):
    def __init__(self) -> None:
        super().__init__()

    def on_moved(self, event: FileSystemEvent) -> None:
        super().on_moved(event)

        what = "directory" if event.is_directory else "file"
        logger.info("Moved {}: from {} to {}", what, event.src_path, event.dest_path)
        self.handle_changes(event)

    def on_created(self, event: FileSystemEvent) -> None:
        super().on_created(event)

        what = "directory" if event.is_directory else "file"
        logger.info("Created {}: {}", what, event.src_path)
        self.handle_changes(event)

    def on_deleted(self, event: FileSystemEvent) -> None:
        super().on_deleted(event)

        what = "directory" if event.is_directory else "file"
        logger.info("Deleted {}: {}", what, event.src_path)
        self.handle_changes(event)

    def on_modified(self, event: FileSystemEvent) -> None:
        super().on_modified(event)

        what = "directory" if event.is_directory else "file"
        logger.info("Modified {}: {}", what, event.src_path)
        self.handle_changes(event)

    def handle_changes(self, event: FileSystemEvent) -> None:
        subprocess.run(["make"])


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "./proto"
    event_handler = EventHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
