from aiohttp import (
    ClientResponseError,
    ClientSession,
    ClientTimeout
)
from base58 import b58decode, b58encode
from nacl.signing import SigningKey
from colorama import *
from datetime import datetime, timezone
from fake_useragent import FakeUserAgent
import asyncio, json, os, pytz

wib = pytz.timezone('Asia/Jakarta')

class Assisterr:
    def __init__(self) -> None:
        self.headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
            "Host": "api.assisterr.ai",
            "Origin": "https://build.assisterr.ai",
            "Referer": "https://build.assisterr.ai/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "User-Agent": FakeUserAgent().random
        }
        self.cookie = "ref=66aa875402ad9bcc9ae1f21a"

    def clear_terminal(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def log(self, message):
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}{message}",
            flush=True
        )

    def welcome(self):
        print(
            f"""
        {Fore.GREEN + Style.BRIGHT}Auto Claim {Fore.BLUE + Style.BRIGHT}Assisterr - BOT
            """
            f"""
        {Fore.GREEN + Style.BRIGHT}Rey? {Fore.YELLOW + Style.BRIGHT}<INI WATERMARK>
            """
        )

    def format_seconds(self, seconds):
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
    
    def mask_account(self, account):
        mask_account = account[:6] + '*' * 6 + account[-6:]
        return mask_account    

    def generate_address(self, account: str):
        try:
            decode_account = b58decode(account)
            signing_key = SigningKey(decode_account[:32])
            verify_key = signing_key.verify_key

            address = b58encode(verify_key.encode()).decode()
            
            return address

        except Exception as e:
            return None

    def generate_payload(self, account: str, address: str, message: str):
        try:
            decode_account = b58decode(account)
            signing_key = SigningKey(decode_account[:32])

            encode_message = message.encode('utf-8')
            signature = signing_key.sign(encode_message)

            signature_base58 = b58encode(signature.signature).decode()

            data = {
                "message": message, 
                "signature": signature_base58, 
                "key": address
            }
            
            return data

        except Exception as e:
            return None
    
    async def get_message(self, retries=5):
        url = "https://api.assisterr.ai/incentive/auth/login/get_message/"
        headers = {
            **self.headers,
            "Cookie": self.cookie
        }
        for attempt in range(retries):
            try:
                async with ClientSession(timeout=ClientTimeout(total=20)) as session:
                    async with session.get(url=url, headers=headers) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue

                return None
    
    async def user_login(self, account: str, address: str, message: str, retries=5):
        url = "https://api.assisterr.ai/incentive/auth/login/"
        data = json.dumps(self.generate_payload(account, address, message))
        headers = {
            **self.headers,
            "Content-Length": str(len(data)),
            "Content-Type": "application/json"
        }
        for attempt in range(retries):
            try:
                async with ClientSession(timeout=ClientTimeout(total=20)) as session:
                    async with session.post(url=url, headers=headers, data=data) as response:
                        response.raise_for_status()
                        result = await response.json()
                        return result['access_token']
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue

                return None
    
    async def user_data(self, token: str, retries=5):
        url = "https://api.assisterr.ai/incentive/users/me/"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        for attempt in range(retries):
            try:
                async with ClientSession(timeout=ClientTimeout(total=20)) as session:
                    async with session.get(url=url, headers=headers) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue

                return None
    
    async def user_meta(self, token: str, retries=5):
        url = "https://api.assisterr.ai/incentive/users/me/meta/"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        for attempt in range(retries):
            try:
                async with ClientSession(timeout=ClientTimeout(total=20)) as session:
                    async with session.get(url=url, headers=headers) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue

                return None
    
    async def claim_daily(self, token: str, retries=5):
        url = "https://api.assisterr.ai/incentive/users/me/daily_points/"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {token}",
            "Connection": "keep-alive",
            "Content-Length": "0",
            "Content-Type": "application/json"
        }
        for attempt in range(retries):
            try:
                async with ClientSession(timeout=ClientTimeout(total=20)) as session:
                    async with session.post(url=url, headers=headers) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue

                return None
        
    async def process_accounts(self, account: str, address: str):
        message = await self.get_message()
        if not message:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}Status  :{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} GET Message Failed {Style.RESET_ALL}"
            )
            return

        token = await self.user_login(account, address, message)
        if not token:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}Status  :{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} Login Failed {Style.RESET_ALL}"
            )
            return
        
        self.log(
            f"{Fore.CYAN+Style.BRIGHT}Status  :{Style.RESET_ALL}"
            f"{Fore.GREEN+Style.BRIGHT} Login Success {Style.RESET_ALL}"
        )

        balance = "N/A"

        user = await self.user_data(token)
        if user:
            balance = user.get("points", 0) / 100
        
        self.log(
            f"{Fore.CYAN+Style.BRIGHT}Balance :{Style.RESET_ALL}"
            f"{Fore.WHITE+Style.BRIGHT} {balance} $ASRR {Style.RESET_ALL}"
        )

        meta = await self.user_meta(token)
        if not meta:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}Check-In:{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} GET Data Failed {Style.RESET_ALL}"
            )
            return

        claim_time = meta.get('daily_points_start_at', None)

        if claim_time is None:
            claim = await self.claim_daily(token)
            if claim:
                balance = claim_wib.get("points", 0) / 100
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Check-In:{Style.RESET_ALL}"
                    f"{Fore.GREEN+Style.BRIGHT} Is Claimed {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.CYAN+Style.BRIGHT} Balance Now {Style.RESET_ALL}"
                    f"{Fore.WHITE+Style.BRIGHT}{balance} $ASRR{Style.RESET_ALL}"
                )
            else:
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Check-In:{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Isn't Claimed {Style.RESET_ALL}"
                )
        else:
            claim_utc = datetime.fromisoformat(claim_time).replace(tzinfo=timezone.utc)
            claim_wib = claim_utc.astimezone(wib).strftime('%x %X %Z')
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}Check-In:{Style.RESET_ALL}"
                f"{Fore.YELLOW+Style.BRIGHT} Is Already Claimed {Style.RESET_ALL}"
                f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                f"{Fore.CYAN+Style.BRIGHT} Next Claim at {Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT}{claim_wib}{Style.RESET_ALL}"
            )

    async def main(self):
        try:
            with open('accounts.txt', 'r') as file:
                accounts = [line.strip() for line in file if line.strip()]
            
            while True:
                self.clear_terminal()
                self.welcome()
                self.log(
                    f"{Fore.GREEN + Style.BRIGHT}Account's Total: {Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT}{len(accounts)}{Style.RESET_ALL}"
                )
                
                separator = "=" * 23
                for account in accounts:
                    if account:
                        address = self.generate_address(account)
                        self.log(
                            f"{Fore.CYAN + Style.BRIGHT}{separator}[{Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT} {self.mask_account(address)} {Style.RESET_ALL}"
                            f"{Fore.CYAN + Style.BRIGHT}]{separator}{Style.RESET_ALL}"
                        )
                        await self.process_accounts(account, address)
                        await asyncio.sleep(3)

                self.log(f"{Fore.CYAN + Style.BRIGHT}={Style.RESET_ALL}"*68)
                seconds = 6 * 60 * 60
                while seconds > 0:
                    formatted_time = self.format_seconds(seconds)
                    print(
                        f"{Fore.CYAN+Style.BRIGHT}[ Wait for{Style.RESET_ALL}"
                        f"{Fore.WHITE+Style.BRIGHT} {formatted_time} {Style.RESET_ALL}"
                        f"{Fore.CYAN+Style.BRIGHT}... ]{Style.RESET_ALL}"
                        f"{Fore.WHITE+Style.BRIGHT} | {Style.RESET_ALL}"
                        f"{Fore.BLUE+Style.BRIGHT}All Accounts Have Been Processed.{Style.RESET_ALL}",
                        end="\r"
                    )
                    await asyncio.sleep(1)
                    seconds -= 1

        except FileNotFoundError:
            self.log(f"{Fore.RED}File 'accounts.txt' Not Found.{Style.RESET_ALL}")
            return
        except Exception as e:
            self.log(f"{Fore.RED+Style.BRIGHT}Error: {e}{Style.RESET_ALL}")

if __name__ == "__main__":
    try:
        bot = Assisterr()
        asyncio.run(bot.main())
    except KeyboardInterrupt:
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
            f"{Fore.RED + Style.BRIGHT}[ EXIT ] Assisterr - BOT{Style.RESET_ALL}                                       "                              
        )