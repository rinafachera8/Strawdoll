import win32api
import win32com.client
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import ctypes
import psutil
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
import logging
import sys
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SystemChecks:
    def is_mouse_present(self):
        try:
            devices = win32api.GetSystemMetrics(43)  # SM_MOUSEPRESENT
            return devices != 0
        except Exception as e:
            logger.warning(f"Error checking for mouse: {e}")
            return False

    #def is_audio_muted(self):
    #    try:
    #        devices = AudioUtilities.GetSpeakers()
    #        interface = devices.Activate(
    #            IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    #        volume = cast(interface, POINTER(IAudioEndpointVolume))
    #        return volume.GetMute()
    #    except Exception as e:
    #        logger.warning(f"Error checking audio status: {e}")
    #        return False

    def check_cpu_cores(self):
        try:
            cores = os.cpu_count()
            if cores <= 1:  # This would be unusual for a modern physical machine
                return False
            return True
        except Exception as e:
            logger.warning(f"Error checking CPU cores: {e}")
            return False

    def check_gpu(self):
        try:
            wmi = win32com.client.Dispatch("WbemScripting.SWbemLocator")
            wm_instance = wmi.ConnectServer(".", "root\cimv2")
            gpus = wm_instance.ExecQuery("Select * from Win32_VideoController")
            for gpu in gpus:
                if "microsoft" in gpu.Name.lower():
                    return False
            return True
        except Exception as e:
            logger.warning(f"Error checking GPU: {e}")
            return False

    def check_memory(self):
        try:
            virtual_memory = psutil.virtual_memory()
            total_memory = virtual_memory.total  # total physical memory available
            
            #logger.info(f"Total Memory: {total_memory / (1024**3)} GB")
            
            if total_memory <= 2 * 1024 ** 3:  # Check for less than or equal to 2GB RAM
                return False
            return True
        except Exception as e:
            logger.warning(f"Error checking memory using psutil: {e}")
            return False

    def run_system_checks(self) -> bool:
        if not self.is_mouse_present():
            logger.error("No mouse detected!")
            return True


        # if self.is_audio_muted():
        #     logger.error("Audio is muted!")
        #     return True

        if not self.check_cpu_cores():
            logger.error("Unusual number of CPU cores detected!")
            return True

        if not self.check_gpu():
            logger.error("Virtual GPU or default Microsoft GPU detected!")
            return True

        if not self.check_memory():
            logger.error("Low system memory detected!")
            return True

        return False
