import logging
from psutil import process_iter, NoSuchProcess, AccessDenied, ZombieProcess

logging.basicConfig(level=logging.INFO)

class ForbiddenProcessCheck:
    """Class to check for and terminate unwanted processes."""
    
    def __init__(self):
        self.forbidden_processes = [
            'http', 'traffic', 'wireshark', 'fiddler', 'packet', 
            'charles', 'burpsuite', 'ollydbg', 'x32dbg', 'x64dbg', 
            'idapro', 'idaq', 'ida64', 'jadx', 'ghidra', 'radare2', 
            'cheatengine', 'memscan', 'artmoney', 'gameconqueror', 
            'debugger', 'windbg'
        ]

    def add_forbidden_process(self, process_name: str):
        """Add a new forbidden process to the list."""
        self.forbidden_processes.append(process_name.lower())

    def remove_forbidden_process(self, process_name: str):
        """Remove a forbidden process from the list."""
        self.forbidden_processes.remove(process_name.lower())

    def _terminate_forbidden_processes(self):
        """Terminate all forbidden processes."""
        for proc in process_iter():
            try:
                for name in self.forbidden_processes:
                    if name in proc.name().lower():
                        proc.kill()
                        logging.info(f"Terminated process: {proc.name()}")
            except (NoSuchProcess, AccessDenied, ZombieProcess) as e:
                logging.error(f"Error handling process {proc.name()}: {e}")

    def run_checks(self):
        """Check for forbidden processes and terminate them."""
        logging.info("Running forbidden process check...")
        self._terminate_forbidden_processes()
