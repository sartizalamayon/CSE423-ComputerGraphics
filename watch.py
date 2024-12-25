from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import os
import time
import subprocess

class Watcher:
    DIRECTORY_TO_WATCH = os.path.dirname(os.path.abspath(__file__))

    def __init__(self, script_name):
        self.observer = Observer()
        self.script_name = script_name

    def run(self):
        event_handler = Handler(self.script_name)
        self.observer.schedule(event_handler, self.DIRECTORY_TO_WATCH, recursive=False)
        self.observer.start()
        print(f"Watching {self.DIRECTORY_TO_WATCH} for changes...")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.observer.stop()
        self.observer.join()

class Handler(FileSystemEventHandler):
    def __init__(self, script_name):
        self.script_name = script_name
        self.process = None
        self.run_script()

    def on_modified(self, event):
        if event.src_path.endswith(self.script_name):
            self.restart_script()

    def run_script(self):
        print("\n--- File Changed. Starting Script ---\n")
        if self.process is not None:
            self.process.terminate()  # Stop the existing process
        self.process = subprocess.Popen(["python", self.script_name])

    def restart_script(self):
        print("\n--- File Changed. Restarting Script ---\n")
        self.run_script()

    def __del__(self):
        if self.process is not None:
            self.process.terminate()  # Clean up the process when the handler is destroyed

if __name__ == "__main__":
    script_to_watch = "maze_runner.py"  # Replace with your script name
    watcher = Watcher(script_to_watch)
    watcher.run()
