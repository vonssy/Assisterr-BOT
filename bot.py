from aiohttp import (
    ClientResponseError,
    ClientSession,
    ClientTimeout
)
from aiohttp_socks import ProxyConnector
from fake_useragent import FakeUserAgent
from base58 import b58decode, b58encode
from nacl.signing import SigningKey
from datetime import datetime, timezone
from colorama import *
import asyncio, json, os, pytz

wib = pytz.timezone('Asia/Jakarta')

class Assisterr:
    def __init__(self) -> None:
        self.headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
            "Origin": "https://build.assisterr.ai",
            "Referer": "https://build.assisterr.ai/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "User-Agent": FakeUserAgent().random
        }
        self.proxies = []
        self.proxy_index = 0
        self.account_proxies = {}

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
    
    async def load_proxies(self, use_proxy_choice: int):
        filename = "proxy.txt"
        try:
            if use_proxy_choice == 1:
                async with ClientSession(timeout=ClientTimeout(total=30)) as session:
                    async with session.get("https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/all.txt") as response:
                        response.raise_for_status()
                        content = await response.text()
                        with open(filename, 'w') as f:
                            f.write(content)
                        self.proxies = content.splitlines()
            else:
                if not os.path.exists(filename):
                    self.log(f"{Fore.RED + Style.BRIGHT}File {filename} Not Found.{Style.RESET_ALL}")
                    return
                with open(filename, 'r') as f:
                    self.proxies = f.read().splitlines()
            
            if not self.proxies:
                self.log(f"{Fore.RED + Style.BRIGHT}No Proxies Found.{Style.RESET_ALL}")
                return

            self.log(
                f"{Fore.GREEN + Style.BRIGHT}Proxies Total  : {Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT}{len(self.proxies)}{Style.RESET_ALL}"
            )
        
        except Exception as e:
            self.log(f"{Fore.RED + Style.BRIGHT}Failed To Load Proxies: {e}{Style.RESET_ALL}")
            self.proxies = []

    def check_proxy_schemes(self, proxies):
        schemes = ["http://", "https://", "socks4://", "socks5://"]
        if any(proxies.startswith(scheme) for scheme in schemes):
            return proxies
        return f"http://{proxies}"

    def get_next_proxy_for_account(self, token):
        if token not in self.account_proxies:
            if not self.proxies:
                return None
            proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
            self.account_proxies[token] = proxy
            self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return self.account_proxies[token]

    def rotate_proxy_for_account(self, token):
        if not self.proxies:
            return None
        proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
        self.account_proxies[token] = proxy
        self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return proxy
    
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
        
    def print_question(self):
        while True:
            try:
                print("1. Run With Monosans Proxy")
                print("2. Run With Private Proxy")
                print("3. Run Without Proxy")
                choose = int(input("Choose [1/2/3] -> ").strip())

                if choose in [1, 2, 3]:
                    proxy_type = (
                        "Run With Monosans Proxy" if choose == 1 else 
                        "Run With Private Proxy" if choose == 2 else 
                        "Run Without Proxy"
                    )
                    print(f"{Fore.GREEN + Style.BRIGHT}{proxy_type} Selected.{Style.RESET_ALL}")
                    return choose
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Please enter either 1, 2 or 3.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number (1, 2 or 3).{Style.RESET_ALL}")
    
    async def get_message(self, proxy=None, retries=5):
        url = "https://api.assisterr.ai/incentive/auth/login/get_message/"
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.get(url=url, headers=self.headers) as response:
                        if response.status == 403:
                            return None
                        
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue

                return None
    
    async def user_login(self, account: str, address: str, message: str, proxy=None, retries=5):
        url = "https://api.assisterr.ai/incentive/auth/login/"
        data = json.dumps(self.generate_payload(account, address, message))
        headers = {
            **self.headers,
            "Content-Length": str(len(data)),
            "Content-Type": "application/json"
        }
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers, data=data) as response:
                        response.raise_for_status()
                        result = await response.json()
                        return result['access_token']
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue

                return None
    
    async def user_data(self, token: str, proxy=None, retries=5):
        url = "https://api.assisterr.ai/incentive/users/me/"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {token}"
        }
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.get(url=url, headers=headers) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue

                return None
    
    async def user_meta(self, token: str, proxy=None, retries=5):
        url = "https://api.assisterr.ai/incentive/users/me/meta/"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {token}"
        }
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.get(url=url, headers=headers) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue

                return None
    
    async def claim_daily(self, token: str, proxy=None, retries=5):
        url = "https://api.assisterr.ai/incentive/users/me/daily_points/"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {token}",
            "Connection": "keep-alive",
            "Content-Length": "0",
            "Content-Type": "application/json"
        }
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue

                return None

    # 1. Twitter Follow Task
    async def claim_twitter_follow(self, token: str, proxy=None, retries=5):
        url = "https://api.assisterr.ai/incentive/users/me/permanent_tasks/twitter_follow/"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {token}",
            "Connection": "keep-alive",
            "Content-Type": "application/json"
        }
        data = json.dumps({"proof": "twitter_follow_proof"})  # Add appropriate proof data if needed
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers, data=data) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                return None

    # 2. Telegram Subscribe Task
    async def claim_telegram_subscribe(self, token: str, proxy=None, retries=5):
        url = "https://api.assisterr.ai/incentive/users/me/permanent_tasks/telegram_subscribe/"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {token}",
            "Connection": "keep-alive",
            "Content-Type": "application/json"
        }
        data = json.dumps({"proof": "telegram_subscribe_proof"})  # Add appropriate proof data if needed
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers, data=data) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                return None
    
    # 3. Twitter Like Task
    async def claim_twitter_like(self, token: str, proxy=None, retries=5):
        url = "https://api.assisterr.ai/incentive/users/me/permanent_tasks/twitter_like/"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {token}",
            "Connection": "keep-alive",
            "Content-Type": "application/json"
        }
        data = json.dumps({"proof": "twitter_like_proof"})  # Add appropriate proof data if needed
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers, data=data) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                return None
    
    # 4. Twitter Repost Task
    async def claim_twitter_repost(self, token: str, proxy=None, retries=5):
        url = "https://api.assisterr.ai/incentive/users/me/permanent_tasks/twitter_repost/"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {token}",
            "Connection": "keep-alive",
            "Content-Type": "application/json"
        }
        data = json.dumps({"proof": "twitter_repost_proof"})  # Add appropriate proof data if needed
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers, data=data) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                return None
    
    # 5. DevAI Subscribe Task
    async def claim_devai_subscribe(self, token: str, proxy=None, retries=5):
        url = "https://api.assisterr.ai/incentive/users/me/permanent_tasks/devai_subscribe/"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {token}",
            "Connection": "keep-alive",
            "Content-Type": "application/json"
        }
        data = json.dumps({"proof": "done"})  # Add appropriate proof data if needed
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers, data=data) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                return None
    
    # 6. DexScreener Support Task
    async def claim_dexscreener(self, token: str, proxy=None, retries=5):
        url = "https://api.assisterr.ai/incentive/users/me/permanent_tasks/devai_support/"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {token}",
            "Connection": "keep-alive",
            "Content-Type": "application/json"
        }
        data = json.dumps({"proof": "dexscreener_support_proof", "address": "your_wallet_address"})  # Add appropriate proof data
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers, data=data) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                return None
    
    # 7. DevAI Like and Comment Task
    async def claim_like_and_comment(self, token: str, proxy=None, retries=5):
        url = "https://api.assisterr.ai/incentive/users/me/permanent_tasks/devai_like_comment/"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {token}",
            "Connection": "keep-alive",
            "Content-Type": "application/json"
        }
        data = json.dumps({"proof": "like_comment_proof", "url": "https://example.com/post"})  # Add appropriate proof data
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers, data=data) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                return None
    
    # 8. DevAI Congratulate Task
    async def claim_congratulate(self, token: str, proxy=None, retries=5):
        url = "https://api.assisterr.ai/incentive/users/me/permanent_tasks/devai_congratulate/"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {token}",
            "Connection": "keep-alive",
            "Content-Type": "application/json"
        }
        data = json.dumps({"proof": "congratulate_proof", "url": "https://example.com/post"})  # Add appropriate proof data
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers, data=data) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                return None
    
    # 9. DevAI Telegram Task
    async def claim_devai_telegram(self, token: str, proxy=None, retries=5):
        url = "https://api.assisterr.ai/incentive/users/me/permanent_tasks/devai_telegram/"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {token}",
            "Connection": "keep-alive",
            "Content-Type": "application/json"
        }
        data = json.dumps({"proof": "telegram_proof", "username": "your_telegram_username"})  # Add appropriate proof data
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers, data=data) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                return None

    async def claim_all_tasks(self, token: str, proxy=None):
        tasks = [
            ("Twitter Follow", self.claim_twitter_follow),
            ("Telegram Subscribe", self.claim_telegram_subscribe),
            ("Twitter Like", self.claim_twitter_like),
            ("Twitter Repost", self.claim_twitter_repost),
            ("DevAI Subscribe", self.claim_devai_subscribe),
            ("DexScreener Support", self.claim_dexscreener),
            ("Like & Comment", self.claim_like_and_comment),
            ("Congratulate", self.claim_congratulate),
            ("DevAI Telegram", self.claim_devai_telegram)
        ]
        
        results = {}
        for task_name, task_func in tasks:
            try:
                result = await task_func(token, proxy)
                status = "Claimed" if result else "Failed"
                results[task_name] = status
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Task    :{Style.RESET_ALL}"
                    f"{Fore.WHITE+Style.BRIGHT} {task_name} {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.GREEN+Style.BRIGHT if status == 'Claimed' else Fore.RED+Style.BRIGHT} {status} {Style.RESET_ALL}"
                )
                await asyncio.sleep(2)  # Add a small delay between task claims
            except Exception as e:
                results[task_name] = "Error"
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Task    :{Style.RESET_ALL}"
                    f"{Fore.WHITE+Style.BRIGHT} {task_name} {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Error: {str(e)[:50]} {Style.RESET_ALL}"
                )
        
        return results
        
    async def process_accounts(self, account: str, address: str, use_proxy: bool):
        proxy = self.get_next_proxy_for_account(address) if use_proxy else None

        message = None
        while message is None:
            message = await self.get_message(proxy)
            if not message:
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Status  :{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} GET Message Failed {Style.RESET_ALL}"
                )
                proxy = self.rotate_proxy_for_account(address) if use_proxy else None
                continue

        self.log(
            f"{Fore.CYAN+Style.BRIGHT}Proxy   :{Style.RESET_ALL}"
            f"{Fore.WHITE+Style.BRIGHT} {proxy} {Style.RESET_ALL}"
        )

        token = await self.user_login(account, address, message, proxy)
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

        user = await self.user_data(token, proxy)
        if user:
            balance = user.get("points", 0) / 100
        
        self.log(
            f"{Fore.CYAN+Style.BRIGHT}Balance :{Style.RESET_ALL}"
            f"{Fore.WHITE+Style.BRIGHT} {balance} $ASRR {Style.RESET_ALL}"
        )

        meta = await self.user_meta(token, proxy)
        if not meta:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}Check-In:{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} GET Data Failed {Style.RESET_ALL}"
            )
            return

        claim_time = meta.get('daily_points_start_at', None)

        if claim_time is None:
            claim = await self.claim_daily(token, proxy)
            if claim:
                balance = claim.get("points", 0) / 100
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
        
        # Attempt to claim all available tasks
        self.log(
            f"{Fore.CYAN+Style.BRIGHT}Tasks   :{Style.RESET_ALL}"
            f"{Fore.WHITE+Style.BRIGHT} Attempting to claim all tasks {Style.RESET_ALL}"
        )
        await self.claim_all_tasks(token, proxy)
        
        # Get updated balance after claiming tasks
        user = await self.user_data(token, proxy)
        if user:
            new_balance = user.get("points", 0) / 100
            if new_balance != balance:
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Update  :{Style.RESET_ALL}"
                    f"{Fore.GREEN+Style.BRIGHT} New Balance {Style.RESET_ALL}"
                    f"{Fore.WHITE+Style.BRIGHT}{new_balance} $ASRR {Fore.GREEN+Style.BRIGHT}(+{new_balance - balance}) {Style.RESET_ALL}"
                )

    async def main(self):
        try:
            with open('accounts.txt', 'r') as file:
                accounts = [line.strip() for line in file if line.strip()]
            
            use_proxy_choice = self.print_question()

            while True:
                use_proxy = False
                if use_proxy_choice in [1, 2]:
                    use_proxy = True

                self.clear_terminal()
                self.welcome()
                self.log(
                    f"{Fore.GREEN + Style.BRIGHT}Account's Total: {Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT}{len(accounts)}{Style.RESET_ALL}"
                )

                if use_proxy:
                    await self.load_proxies(use_proxy_choice)
                
                separator = "=" * 23
                for account in accounts:
                    if account:
                        address = self.generate_address(account)
                        self.log(
                            f"{Fore.CYAN + Style.BRIGHT}{separator}[{Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT} {self.mask_account(address)} {Style.RESET_ALL}"
                            f"{Fore.CYAN + Style.BRIGHT}]{separator}{Style.RESET_ALL}"
                        )
                        await self.process_accounts(account, address, use_proxy)
                        await asyncio.sleep(3)

                self.log(f"{Fore.CYAN + Style.BRIGHT}={Style.RESET_ALL}"*68)
                self.log(
                    f"{Fore.GREEN + Style.BRIGHT}All tasks completed for all accounts. Waiting for next cycle.{Style.RESET_ALL}"
                )
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
            self.log(f"{Fore.RED + Style.BRIGHT}File accounts.txt Not Found.{Style.RESET_ALL}")
            return
        except Exception as e:
            self.log(f"{Fore.RED + Style.BRIGHT}An error occurred: {e}{Style.RESET_ALL}")
            return

if __name__ == "__main__":
    assisterr = Assisterr()
    asyncio.run(assisterr.main())
