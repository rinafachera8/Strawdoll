import ctypes
import os
import sys
import random
import hashlib
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AntiDebugger:
    def __init__(self, file_path=__file__):
        self.file_path = file_path
        self.original_code_hash = self.calculate_code_hash()

    def is_debugger_present(self):
        try:
            kernel32 = ctypes.WinDLL("kernel32")

            # Using IsDebuggerPresent
            if kernel32.IsDebuggerPresent():
                return True

            # Using CheckRemoteDebuggerPresent
            h_process = kernel32.GetCurrentProcess()
            b_debugger_present = ctypes.c_bool(False)
            kernel32.CheckRemoteDebuggerPresent(h_process, ctypes.byref(b_debugger_present))

            if b_debugger_present.value:
                return True

        except Exception as e:
            logger.warning(f"Error checking for debugger: {e}")

        return False

    def hardware_breakpoint_detection(self):
        try:
            # Define CONTEXT structure for x86 architecture
            class CONTEXT(ctypes.Structure):
                _fields_ = [
                    ("ContextFlags", ctypes.c_ulong),
                    
                    # Debug registers
                    ("Dr0", ctypes.c_ulong),
                    ("Dr1", ctypes.c_ulong),
                    ("Dr2", ctypes.c_ulong),
                    ("Dr3", ctypes.c_ulong),
                    ("Dr6", ctypes.c_ulong),
                    ("Dr7", ctypes.c_ulong),
                    
                    # General purpose registers
                    ("Eax", ctypes.c_ulong),
                    ("Ecx", ctypes.c_ulong),
                    ("Edx", ctypes.c_ulong),
                    ("Ebx", ctypes.c_ulong),
                    ("Esp", ctypes.c_ulong),
                    ("Ebp", ctypes.c_ulong),
                    ("Esi", ctypes.c_ulong),
                    ("Edi", ctypes.c_ulong),
                    
                    # Segment registers
                    ("SegGs", ctypes.c_ulong),
                    ("SegFs", ctypes.c_ulong),
                    ("SegEs", ctypes.c_ulong),
                    ("SegDs", ctypes.c_ulong),
                    
                    # Control registers
                    ("EFlags", ctypes.c_ulong),
                    ("Eip", ctypes.c_ulong),
                    ("SegCs", ctypes.c_ulong),
                    ("SegSs", ctypes.c_ulong),
                    
                    # Extended registers (MMX, SSE, etc.)
                    ("ExtendedRegisters", ctypes.c_ubyte * 512)
                ]

            context = CONTEXT()
            context.ContextFlags = 0x10  # CONTEXT_DEBUG_REGISTERS

            kernel32 = ctypes.WinDLL("kernel32")
            h_thread = kernel32.GetCurrentThread()

            if kernel32.GetThreadContext(h_thread, ctypes.byref(context)):
                if context.Dr0 or context.Dr1 or context.Dr2 or context.Dr3:
                    return True

        except Exception as e:
            logger.warning(f"Error during hardware breakpoint detection: {e}")
            return False

        return False

    def check_debugger_process_name(self):
        try:
            import psutil
            parent = psutil.Process(os.getppid())
            known_debugger_names = ['gdb', 'ida', 'x64dbg', 'ollydbg']
            return parent.name().lower() in known_debugger_names
        except Exception as e:
            logger.warning(f"Error checking debugger process name: {e}")
            return False
        
    def calculate_code_hash(self):
        hasher = hashlib.sha256()
        try:
            with open(self.file_path, 'rb') as file:
                for chunk in iter(lambda: file.read(65536), b''):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except Exception as e:
            logger.warning(f"Error calculating code hash: {e}")
            return None

    def run_anti_debugging_checks(self):
        logger.info("Anti-Debugger check running")

        if self.is_debugger_present():
            logger.error("API-based debugger detection triggered!")
            return True

        if self.hardware_breakpoint_detection():
            logger.error("Hardware breakpoint detected!")
            return True

        if self.check_debugger_process_name():
            logger.error("Debugger process name detected!")
            return True

        current_code_hash = self.calculate_code_hash()
        if self.original_code_hash != current_code_hash:
            logger.error("Code modification detected!")
            return True

        return False

