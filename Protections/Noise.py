import asyncio
import random
import logging
import aiofiles
import os
import math
import tempfile
import atexit
import shutil
import string

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NoiseGenerator:

    @staticmethod
    async def create_noise():
        logger.info("Noise generation started...")
        
        while True:
            try:
                # Dynamic noise length
                length = random.randint(500, 1500)
                noise = [random.randint(0, 255) for _ in range(length)]
                
                # More operations
                operations = [
                    lambda i: noise[i] ^ noise[i - 1],
                    lambda i: (noise[i] + noise[i - 1]) & 0xFF,
                    lambda i: (noise[i] ^ noise[i - 1] ^ 0xAA) & 0xFF,
                    lambda i: ((noise[i] << 1) ^ 0x55) & 0xFF,
                    lambda i: (noise[i] + 2*noise[i - 1]) & 0xFF,
                    lambda i: ((noise[i] >> 2) ^ 0xAA) & 0xFF
                ]
                
                for op in operations:
                    for i in range(1, len(noise)):
                        noise[i] = op(i)

                #log activity
                logger.info("Noise generation active...")

                # Variable sleep interval
                sleep_time = random.uniform(0.5, 1.5)
                await asyncio.sleep(sleep_time)

            except Exception as e:
                logger.error(f"Error in noise generation: {e}")
                await asyncio.sleep(1)  # Introducing a short sleep before retrying

    @staticmethod
    async def create_alternate_noise():
        logger.info("Alternate noise generation started...")
        
        while True:
            try:
                # Dynamic noise length
                length = random.randint(200, 500)
                noise = [random.randint(0, 127) for _ in range(length)]

                # Different operations
                operations = [
                    lambda i: (noise[i] ^ 0x33) & 0xFF,
                    lambda i: (noise[i] + 3*noise[i - 1]) & 0xFF,
                    lambda i: (noise[i] ^ noise[i - 1] ^ 0x77) & 0xFF,
                    lambda i: ((noise[i] >> 1) ^ 0x11) & 0xFF
                ]
                
                for op in operations:
                    for i in range(1, len(noise)):
                        noise[i] = op(i)

                # log activity
                logger.info("Alternate noise generation active...")

                # Variable sleep interval
                sleep_time = random.uniform(0.7, 1.2)
                await asyncio.sleep(sleep_time)

            except Exception as e:
                logger.error(f"Error in alternate noise generation: {e}")
                await asyncio.sleep(1.2) 

    @staticmethod
    async def read_random_files():
        logger.info("Random file reading started...")

        # Use the user's home directory as the root to limit the scope
        root_dir = os.path.expanduser("~")

        # Get a list of all files in the root directory and its subdirectories
        all_files = [os.path.join(dp, f) for dp, dn, filenames in os.walk(root_dir) for f in filenames]

        # Limit the number of files to consider
        max_files_to_consider = 100
        if len(all_files) > max_files_to_consider:
            all_files = random.sample(all_files, max_files_to_consider)

        max_file_size = 1 * (1024 ** 2)  # 1MB limit

        while True:
            start_time = asyncio.get_event_loop().time()
            while asyncio.get_event_loop().time() - start_time < random.uniform(0.05, 0.2):
                try:
                    # Randomly select a file
                    random_file = random.choice(all_files)

                    # Check the file size
                    if os.path.getsize(random_file) > max_file_size:
                        logger.warning(f"Skipped large file: {random_file}")
                        continue

                    # Read the file
                    async with aiofiles.open(random_file, 'rb') as file:
                        _ = await file.read()

                except Exception as e:
                    logger.error(f"Error reading random file: {e}")

            await asyncio.sleep(5)  # Pause for 5 seconds before the next iteration

    @staticmethod
    async def random_string_generator():
        logger.info("Random string generation started...")

        characters = (
            "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
            "!@#$%^&*()-_=+[]{}|;:',.<>?/`~"  # Common symbols
            "©®¶•ªº°"  # Some special characters
            "😀😃😄😁😆😅😂🤣😊😇🙂😉😌😍🤩🥳🦄🌈🍀🌍🌑🌒🌓🌔🌕🌖🌗🌘🌙🌚🌛🌜🌝🎍🎋🎎🎏🎐🎑🎒🎓🎖🎗🎘🎙🎚🎛🎜🎝🎞🎟🎠🎡🎢🎣🎤🎥🎦🎧🎨🎩🎪🎫🎬🎭🎮🎯🎰🎱🎲🎳🎴🎵🎶🎷🎸🎹🎺🎻🎼🎽🎾🎿🏀🏁🏂🏃🏄🏅🏆🏇🏈🏉🏊🏋🏌🏍🏎🏏🏐🏑🏒🏓🏔🏕🏖🏗🏘🏙🏚🏛🏜🏝🏞🏟🏠🏡🏢🏣🏤🏥🏦🏧🏨🏩🏪🏫🏬🏭🏮🏯🏰🏱🏲🏳🏴🏵🏶🏷🏸🏹🏺🏻🏼🏽🏾🏿🐀🐁🐂🐃🐄🐅🐆🐇🐈🐉🐊🐋🐌🐍🐎🐏🐐🐑🐒🐓🐔🐕🐖🐗🐘🐙🐚🐛🐜🐝🐞🐟🐠🐡🐢🐣🐤🐥🐦🐧🐨🐩🐪🐫🐬🐭🐮🐯🐰🐱🐲🐳🐴🐵🐶🐷🐸🐹🐺🐻🐼🐽🐾🐿👀👁👂👃👄👅👆👇👈👉👊👋👌👍👎👏👐👑👒👓👔👕👖👗👘👙👚👛👜👝👞👟👠👡👢👣👤👥👦👧👨👩👪👫👬👭👮👯👰👱👲👳👴👵👶👷👸👹👺👻👼👽👾👿💀💁💂💃💄💅💆💇💈💉💊💋💌💍💎💏💐💑💒💓💔💕💖💗💘💙💚💛💜💝💞💟💠💡💢💣💤💥💦💧💨💩💪💫💬💭💮💯💰💱💲💳💴💵💶💷💸💹💺💻💼💽💾💿📀📁📂📃📄📅📆📇📈📉📊📋📌📍📎📏📐📑📒📓📔📕📖📗📘📙📚📛📜📝📞📟📠📡📢📣📤📥📦📧📨📩📪📫📬📭📮📯📰📱📲📳📴📵📶📷📸📹📺📻📼📽📿🔀🔁🔂🔃🔄🔅🔆🔇🔈🔉🔊🔋🔌🔍🔎🔏🔐🔑🔒🔓🔔🔕🔖🔗🔘🔙🔚🔛🔜🔝🔞🔟🔠🔡🔢🔣🔤🔥🔦🔧🔨🔩🔪🔫🔬🔭🔮🔯🔰🔱🔲🔳🔴🔵🔶🔷🔸🔹🔺🔻🔼🔽🕀🕁🕂🕃🕄🕅🕆🕇🕈🕉🕊🕋🕌🕍🕎🕏🕐🕑🕒🕓🕔🕕🕖🕗🕘🕙🕚🕛🕜🕝🕞🕟🕠🕡🕢🕣🕤🕥🕦🕧🕯🕰🕱🕲🕳🕴🕵🕶🕷🕸🕹🕺🕻🕼🕽🕾🕿🖀🖁🖂🖃"  # Emojis (you can add more as needed)
        )

        while True:
            try:
                string_length = random.randint(11, 1057)
                random_string = ''.join(random.choice(characters) for _ in range(string_length))
                
                #logger.info(f"Generated random string: {random_string}")

                # Variable sleep interval
                sleep_time = random.uniform(0.4, 0.9)
                await asyncio.sleep(sleep_time)

            except Exception as e:
                logger.error(f"Error in random string generation: {e}")
                await asyncio.sleep(1)

    @staticmethod
    async def math_noise():
        logger.info("Math noise generation started...")

        while True:
            try:
                num1 = random.randint(1, 1000)
                num2 = random.randint(1, 1000)
                num3 = random.randint(1, 100)
                
                # Complex math operations
                result1 = num1 * math.sin(num2) + math.sqrt(num1) - math.pow(num2, num3 % 5) 
                result2 = math.factorial(num3 % 10)  # Factorial operation for values between 0 and 9
                result3 = math.log(num1 + 2) * math.tan(num2 - 1) - math.pow(num1, 2.71828)  # Using Euler's number

                prime_check = all(num3 % i != 0 for i in range(2, int(math.sqrt(num3)) + 1))  # Check if num3 is prime

                #logger.info(f"Math operation results: {result1}, {result2}, {result3}, Prime: {prime_check}")

                # Variable sleep interval
                sleep_time = random.uniform(0.5, 1.0)
                await asyncio.sleep(sleep_time)

            except Exception as e:
                logger.error(f"Error in math noise generation: {e}")
                await asyncio.sleep(1)

    @staticmethod
    async def activity_simulation():
        logger.info("Activity simulation started...")

        # Mock database tables and fields for our fake queries
        mock_tables = ["users", "orders", "products"]
        mock_fields = {
            "users": ["id", "name", "email"],
            "orders": ["id", "user_id", "product_id", "date"],
            "products": ["id", "name", "price"]
        }

        while True:
            try:
                # Randomly decide the type of user action: login, registration, or data retrieval
                user_action = random.choice(["login", "registration", "data_retrieval"])

                if user_action == "login":
                    # Simulate a user login
                    username = f"user{random.randint(1, 1000)}"
                    logger.info(f"User '{username}' logged in")

                elif user_action == "registration":
                    # Simulate a user registration
                    new_user_id = random.randint(10, 2000)
                    username = f"user{new_user_id}"
                    logger.info(f"New user '{username}' registered")

                elif user_action == "data_retrieval":
                    # Simulate data retrieval by a user
                    table = random.choice(mock_tables)
                    fields = mock_fields[table]
                    query = f"SELECT {', '.join(fields)} FROM {table} WHERE {fields[0]} = {random.randint(1, 1000)}"
                    logger.info(f"User requested data: {query}")

                # Variable sleep interval
                sleep_time = random.uniform(0.1, 0.5)
                await asyncio.sleep(sleep_time)

            except Exception as e:
                logger.error(f"Error in activity simulation: {e}")
                await asyncio.sleep(1)
