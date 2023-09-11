import logging
import subprocess

class BIOSVersionChecker:

    def __init__(self):
        self.vm_bios_strings = [
            "virtualbox", "vbox", "innotek gmbh",
            "vmware", "vmw",
            "hyperv", "bhyve bhyve", "microsoft hv",
            "qemu", "bochs",
            "xen", "xensource",
            "parallels", "prl hypervisor",
            "rhev hypervisor",
            "ovm",
            "sandboxie",
            "virtualpc"
        ]

    def _check_bios_version(self):
        """Check BIOS version and description and alert if VM-specific strings are found."""
        try:
            version_result = subprocess.check_output(["wmic", "bios", "get", "smbiosbiosversion"], universal_newlines=True)
            description_result = subprocess.check_output(["wmic", "bios", "get", "description"], universal_newlines=True)

            bios_version = version_result.strip().split("\n")[-1].lower()
            bios_description = description_result.strip().split("\n")[-1].lower()

            logging.info(f"Current BIOS version: {bios_version}")
            logging.info(f"Current BIOS description: {bios_description}")

            for vm_string in self.vm_bios_strings:
                if vm_string in bios_version or vm_string in bios_description:
                    logging.warning(f"VM detected based on BIOS version or description: {bios_version} | {bios_description}")
                    return True

        except Exception as e:
            logging.error(f"Error checking BIOS version or description: {e}")
            return True  # We treat errors as check failures for safety

        return False

    def run_checks(self):
        return self._check_bios_version()
