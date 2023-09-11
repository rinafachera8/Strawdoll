import logging
import cpuinfo
import subprocess

class NestedVirtualizationChecker:

    def __init__(self):
        # Known hypervisor vendor IDs
        self.known_hypervisor_ids = [
            "VMwareVMware",         # VMware
            "KVMKVMKVM",            # KVM
            "Microsoft Hv",         # Microsoft Hyper-V or Windows Hypervisor Platform
            "XenVMMXenVMM",         # Xen
            "prl hyperv",           # Parallels Desktop
            "VBoxVBoxVBox",         # VirtualBox
            "OracleVM VirtualBox",  # VirtualBox
            "lrpepyh vr",           # Reverse of "hyperv lrpepyh vr"
            "VMW",                  # VMware
            "XenVMM",               # Xen (again, for redundancy)
            "QEMU"                  # QEMU (not always detectable via this method)
        ]
        self.hyper_v_processes = [
            "vmms.exe",             # Hyper-V Virtual Machine Management Service
            "vmwp.exe",             # Hyper-V Worker Process (one for each VM)
            "vmcompute.exe",        # Hyper-V Host Compute Service (related to containers & Hyper-V)
            "vmbus.sys",            # Hyper-V VMBus
            "vmicrdv.sys",          # Hyper-V Integration Device Redirector
            "vmicvss.sys",          # Hyper-V Volume Shadow Copy Requestor
            "vmicshutdown.sys",     # Hyper-V Integration Shutdown Service
            "vmicheartbeat.sys",    # Hyper-V Integration Heartbeat Service
            "vmicexchange.sys",     # Hyper-V Integration Time Synchronization Service
            "vmicheartbeat.sys",    # Hyper-V Integration Heartbeat Service
            "vmickvpexchange.sys",  # Hyper-V Data Exchange Integration Service
            "vmicrdv.sys",          # Hyper-V Integration Device Redirector
            "vmicres.dll",          # Hyper-V Replica
            "vmictimesync.sys",     # Hyper-V Time Synchronization Service
            "vmgid.sys",            # Hyper-V Guest Infrastructure Driver
            "vmicguestinterface.sys",# Hyper-V Guest Interface
            "hvax64.exe",           # Hyper-V UEFI Virtual Firmware
            "hvboot.sys",           # Hyper-V Hypervisor Boot Service
            "hvhostsvc.exe",        # Hyper-V Host Compute Service
            "hvsirpcd.exe",         # Hyper-V Integration Remote Procedure Call Service
            "hvix64.exe"            # Hyper-V UEFI Virtual Firmware (ARM64)
        ]

    def check_nested_virtualization(self):
        logging.info("Starting nested virtualization check...")

        try:
            info = cpuinfo.get_cpu_info()
            vendor_id = info.get('vendor_id_raw', '')
            
            if not vendor_id:
                return False
            
            if vendor_id in self.known_hypervisor_ids:
                logging.info(f"Running inside a VM by {vendor_id}. Checking for nested virtualization...")
                
                # If detected as a VM by CPUID check, proceed with Windows-specific checks.
                if self.check_hyper_v_processes():
                    logging.warning("Nested virtualization suspected: Detected Hyper-V processes while inside a VM.")
                    return True
                
                if self.check_hyper_v_role():
                    logging.warning("Nested virtualization suspected: Detected Hyper-V role while inside a VM.")
                    return True

        except Exception as e:
            logging.error(f"Error checking for nested virtualization: {e}")
            return True  # Treat errors as check failures for safety

        return False

    def check_hyper_v_processes(self):
        try:
            running_processes = subprocess.check_output("tasklist").decode()
            for process in self.hyper_v_processes:
                if process in running_processes:
                    logging.info(f"Detected Hyper-V process: {process}")
                    return True
        except Exception as e:
            logging.error(f"Error checking for Hyper-V processes: {e}")
            return False
        return False

    def check_hyper_v_role(self):
        try:
            # Check if Hyper-V role is installed
            result = subprocess.check_output("dism /online /get-features /format:table | findstr Microsoft-Hyper-V", shell=True).decode()
            if "Enabled" in result:
                logging.info("Hyper-V role is enabled on this system.")
                return True
        except Exception as e:
            logging.error(f"Error checking for Hyper-V role: {e}")
            return False
        return False

    def run_checks(self):
        return self.check_nested_virtualization() or self.check_hyper_v_processes() or self.check_hyper_v_role()
