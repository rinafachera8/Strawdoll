import os
import winreg
import logging
import subprocess

class WindowsSandboxChecker:

    def __init__(self):
        self.sandbox_processes = [
            "CExecSvc.exe",  # Container Execution Service, specific to Windows Sandbox
            "Vmmem",         # Process managing memory of a Windows Sandbox or Windows Defender Application Guard
            "WsmAgent.exe"   # Windows Sandbox Agent
        ]

        self.sandbox_files = [
            "C:\\windows\\system32\\MacHALDriver.sys",  # Specific driver for Windows Sandbox
            "C:\\sandbox",                              # Default directory structure in Windows Sandbox
            "C:\\Users\\WDAGUtilityAccount"             # Default user for Windows Defender Application Guard
        ]

        self.sandbox_registry_keys = [
            "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Containers\\BaseImages",  # Specific key indicating base images for containers, including Windows Sandbox
            "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Containers\\Runtime"     # Specific key indicating runtime details for containers
        ]

    @staticmethod
    def registry_key_exists(hive, subkey):
        try:
            with winreg.OpenKey(hive, subkey):
                return True
        except FileNotFoundError:
            return False
        
    def check_for_sandbox_registry_keys(self):
        for key in self.sandbox_registry_keys:
            hive_str, subkey = key.split("\\", 1)
            hive = getattr(winreg, hive_str)
            if WindowsSandboxChecker.registry_key_exists(hive, subkey): 
                logging.warning(f"Detected potential sandbox registry key: {key}")
                return True
        return False

    def check_for_sandbox_processes(self):
        logging.info("Starting Windows Sandbox checks...")

        try:
            running_processes = subprocess.check_output("tasklist").decode()
            for process in self.sandbox_processes:
                if process in running_processes:
                    logging.warning(f"Detected Windows Sandbox process: {process}")
                    return True
        except Exception as e:
            logging.error(f"Error checking for Windows Sandbox processes: {e}")
            return True  # Treat errors as check failures for safety

        return False
    
    def check_for_sandbox_files(self):
        try:
            for file_path in self.sandbox_files:
                if os.path.exists(file_path):
                    logging.warning(f"Detected Windows Sandbox file: {file_path}")
                    return True
        except Exception as e:
            logging.error(f"Error checking for Windows Sandbox files: {e}")
            return True  # Treat errors as check failures for safety

        return False


    def run_checks(self):
        return self.check_for_sandbox_processes() or self.check_for_sandbox_files() or self.check_for_sandbox_registry_keys()


