import os
import mmap
import tempfile
import shutil
import win32api
import win32con
import win32file
import logging

logging.basicConfig(level=logging.INFO)

class StealthyFileReader:

    def __init__(self, file_path, encoding="utf-8"):
        self.file_path = file_path
        self.encoding = encoding
        self.method_used = "Not yet determined"

    def _write_and_read_from_memory_map(self, content):
        """Write the content to a memory-mapped file and then read it."""
        try:
            with mmap.mmap(-1, len(content)) as mmapped_file:
                mmapped_file.write(content)
                mmapped_file.seek(0)
                return mmapped_file.read()
        except Exception as e:
            logging.error(f"Failed in memory-mapped operations: {e}")
            raise

    def _handle_read(self):
        try:
            handle = win32file.CreateFile(self.file_path, win32con.GENERIC_READ, win32con.FILE_SHARE_READ, None, win32con.OPEN_EXISTING, 0, None)
            dup_handle = win32api.DuplicateHandle(win32api.GetCurrentProcess(), handle, win32api.GetCurrentProcess(), 0, 0, win32con.DUPLICATE_SAME_ACCESS)
            _, content = win32file.ReadFile(dup_handle, os.path.getsize(self.file_path))
            handle.Close()
            dup_handle.Close()
            self.method_used = "Handle-based Read"
            return content
        except Exception as e:
            logging.error(f"Handle-based read failed: {e}")

    def _memory_map_read(self):
        with open(self.file_path, "rb") as file, mmap.mmap(file.fileno(), 0, access=mmap.ACCESS_READ) as mmapped_file:
            content = mmapped_file.read()
        self.method_used = "Memory Map Read"
        return content

    def _copy_and_read(self):
        with tempfile.NamedTemporaryFile(delete=True) as tmp_file:
            shutil.copy(self.file_path, tmp_file.name)
            content = tmp_file.read()
        self.method_used = "Copy and Read"
        return content

    def _traditional_read(self):
        with open(self.file_path, "rb") as file:
            content = file.read()
        self.method_used = "Traditional Read"
        return content

    def read(self):
        reading_methods = [self._handle_read, self._memory_map_read, self._copy_and_read, self._traditional_read]
        for method in reading_methods:
            content = method()
            if content:
                return self._write_and_read_from_memory_map(content)
        return b""

    def read_text(self):
        return self.read().decode(self.encoding)
    
"""
if __name__ == "__main__":
    login_file = os.path.join("your_file.txt")
    reader = StealthyFileReader(login_file)
    content = reader.read_text()

    print(f"Method used: {reader.method_used}")
    print(content or "Failed to read the file.")
"""