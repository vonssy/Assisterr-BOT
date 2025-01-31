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
    
    def hide_account(self, account):
        hide_account = account[:3] + '*' * 3 + account[-3:]
        return hide_account    

    async def generate_payload(self, account: str, message: str):
        try:
            decode_account = b58decode(account)
            signing_key = SigningKey(decode_account[:32])
            verify_key = signing_key.verify_key

            encode_message = message.encode('utf-8')
            signature = signing_key.sign(encode_message)

            signature_base58 = b58encode(signature.signature).decode()
            public_key = b58encode(verify_key.encode()).decode()
            
            return signature_base58, public_key

        except Exception as e:
            return None, None
    
    async def get_message(self):
        url = "https://api.assisterr.ai/incentive/auth/login/get_message/"
        headers = {
            **self.headers,
            "Cookie": self.cookie
        }
        try:
            async with ClientSession(timeout=ClientTimeout(total=20)) as session:
                async with session.get(url=url, headers=headers) as response:
                    response.raise_for_status()
                    return await response.json()
        except (Exception, ClientResponseError) as e:
            return None
    
    async def user_login(self, message: str, signature: str, key: str):
        url = "https://api.assisterr.ai/incentive/auth/login/"
        data = json.dumps({"message":message, "signature":signature, "key":key})
        headers = {
            **self.headers,
            "Content-Length": str(len(data)),
            "Content-Type": "application/json"
        }
        try:
            async with ClientSession(timeout=ClientTimeout(total=20)) as session:
                async with session.post(url=url, headers=headers, data=data) as response:
                    response.raise_for_status()
                    return await response.json()
        except (Exception, ClientResponseError) as e:
            return None
    
    async def refresh_token(self, access_token: str, refresh_token: str):
        url = "https://api.assisterr.ai/incentive/auth/refresh_token/"
        data = json.dumps({"refresh_token":refresh_token})
        headers = {
            **self.headers,
            "Authorization": f"Bearer {access_token}",
            "Content-Length": str(len(data)),
            "Content-Type": "application/json"
        }
        try:
            async with ClientSession(timeout=ClientTimeout(total=20)) as session:
                async with session.post(url=url, headers=headers, data=data) as response:
                    response.raise_for_status()
                    result = await response.json()
                    return result['access_token']
        except (Exception, ClientResponseError) as e:
            return None
    
    async def user_data(self, access_token: str):
        url = "https://api.assisterr.ai/incentive/users/me/"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        try:
            async with ClientSession(timeout=ClientTimeout(total=20)) as session:
                async with session.get(url=url, headers=headers) as response:
                    response.raise_for_status()
                    return await response.json()
        except (Exception, ClientResponseError) as e:
            return None
    
    async def user_meta(self, access_token: str):
        url = "https://api.assisterr.ai/incentive/users/me/meta/"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        try:
            async with ClientSession(timeout=ClientTimeout(total=20)) as session:
                async with session.get(url=url, headers=headers) as response:
                    response.raise_for_status()
                    return await response.json()
        except (Exception, ClientResponseError) as e:
            return None
    
    async def claim_daily(self, access_token: str):
        url = "https://api.assisterr.ai/incentive/users/me/daily_points/"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {access_token}",
            "Connection": "keep-alive",
            "Content-Length": "0",
            "Content-Type": "application/json"
        }
        try:
            async with ClientSession(timeout=ClientTimeout(total=20)) as session:
                async with session.post(url=url, headers=headers) as response:
                    response.raise_for_status()
                    return await response.json()
        except (Exception, ClientResponseError) as e:
            return None
        
    async def process_accounts(self, account: str):
        hide_account = self.hide_account(account)
        message = await self.get_message()
        if not message:
            self.log(
                f"{Fore.RED + Style.BRIGHT}ERROR:{Style.RESET_ALL}"
                f"{Fore.YELLOW + Style.BRIGHT} GET Message Failed. {Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT}Assisterr Server Maybe Down{Style.RESET_ALL}"
            )
            return
        
        signature, key = await self.generate_payload(account, message)
        if not signature or not key:
            self.log(
                f"{Fore.MAGENTA + Style.BRIGHT}[ Account{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} {hide_account} {Style.RESET_ALL}"
                f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                f"{Fore.RED + Style.BRIGHT} Generate Payload Failed. {Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT}Your Secret Key Maybe Invalid.{Style.RESET_ALL}"
                f"{Fore.MAGENTA + Style.BRIGHT} ]{Style.RESET_ALL}"
            )
            return

        login = await self.user_login(message, signature, key)
        if not login:
            self.log(
                f"{Fore.MAGENTA + Style.BRIGHT}[ Account{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} {hide_account} {Style.RESET_ALL}"
                f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                f"{Fore.RED + Style.BRIGHT} Login Failed {Style.RESET_ALL}"
                f"{Fore.MAGENTA + Style.BRIGHT}]{Style.RESET_ALL}"
            )
            return
        
        access_token = login['access_token']
        refresh_token = login['refresh_token']

        user = await self.user_data(access_token)
        if not user:
            self.log(
                f"{Fore.MAGENTA + Style.BRIGHT}[ Account{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} {login['user']['username']} {Style.RESET_ALL}"
                f"{Fore.RED + Style.BRIGHT}Data Is None{Style.RESET_ALL}"
                f"{Fore.MAGENTA + Style.BRIGHT} ]{Style.RESET_ALL}"
            )
            return

        self.log(
            f"{Fore.MAGENTA + Style.BRIGHT}[ Account{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} {user['username']} {Style.RESET_ALL}"
            f"{Fore.MAGENTA + Style.BRIGHT}] [ Balance{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} {user['points']/100} $ASRR {Style.RESET_ALL}"
            f"{Fore.MAGENTA + Style.BRIGHT}]{Style.RESET_ALL}"
        )
        await asyncio.sleep(1)

        meta = await self.user_meta(access_token)
        if meta:
            claim_time = meta['daily_points_start_at']
            if claim_time is None:
                check_in = await self.claim_daily(access_token)
                if check_in:
                    self.log(
                        f"{Fore.MAGENTA + Style.BRIGHT}[ Check-In{Style.RESET_ALL}"
                        f"{Fore.GREEN + Style.BRIGHT} Is Claimed {Style.RESET_ALL}"
                        f"{Fore.MAGENTA + Style.BRIGHT}] [ Balance{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} {check_in['points']/100} $ASRR {Style.RESET_ALL}"
                        f"{Fore.MAGENTA + Style.BRIGHT}]{Style.RESET_ALL}"
                    )
                else:
                    self.log(
                        f"{Fore.MAGENTA + Style.BRIGHT}[ Check-In{Style.RESET_ALL}"
                        f"{Fore.RED + Style.BRIGHT} Isn't Claimed {Style.RESET_ALL}"
                        f"{Fore.MAGENTA + Style.BRIGHT}]{Style.RESET_ALL}"
                    )
            else:
                claim_utc = datetime.fromisoformat(claim_time).replace(tzinfo=timezone.utc)
                claim_wib = claim_utc.astimezone(wib).strftime('%x %X %Z')
                self.log(
                    f"{Fore.MAGENTA + Style.BRIGHT}[ Check-In{Style.RESET_ALL}"
                    f"{Fore.YELLOW + Style.BRIGHT} Not Time to Claim {Style.RESET_ALL}"
                    f"{Fore.MAGENTA + Style.BRIGHT}] [ Claim at{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} {claim_wib} {Style.RESET_ALL}"
                    f"{Fore.MAGENTA + Style.BRIGHT}]{Style.RESET_ALL}"
                )
        else:
            self.log(
                f"{Fore.MAGENTA + Style.BRIGHT}[ Check-In{Style.RESET_ALL}"
                f"{Fore.RED + Style.BRIGHT} Data Is None {Style.RESET_ALL}"
                f"{Fore.MAGENTA + Style.BRIGHT}]{Style.RESET_ALL}"
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
                self.log(f"{Fore.CYAN + Style.BRIGHT}-{Style.RESET_ALL}"*75)
                
                for account in accounts:
                    account = account.strip()
                    if account:
                        await self.process_accounts(account)
                        self.log(f"{Fore.CYAN + Style.BRIGHT}-{Style.RESET_ALL}"*75)
                        await asyncio.sleep(3)

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