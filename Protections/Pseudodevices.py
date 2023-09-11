import os
import logging

class PseudoDevices:
    def __init__(self):
        self.vm_indicators = [
            "/dev/vboxdrv",  # VirtualBox
            "/dev/vmmon",    # VMware
            "/dev/vmci",     # VMware
            "/dev/kvm",      # KVM (also used by QEMU)
            "/dev/xen/evtchn",  # Xen
        ]

    def detect_vm_via_pseudo_devices(self):
        """Method to detect VMs using pseudo devices."""
        logging.info("Starting PseudoDevices check...")
        
        try:
            detected_devices = [device for device in self.vm_indicators if os.path.exists(device)]
            
            if detected_devices:
                logging.warning(f"Detected VM via pseudo devices: {', '.join(detected_devices)}")
                return True

        except Exception as e:
            logging.error(f"Error checking pseudo devices: {e}")
            return True  # Treat errors as check failures for safety

        return False

    def run_checks(self):
        return self.detect_vm_via_pseudo_devices()
