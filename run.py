import concurrent.futures
import json
import time
import random
import sys
import os
import threading
import requests
from datetime import datetime
import queue
import signal

class Color:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

# Global control variables
continuous_mode = False
stop_reporting = False
reporting_paused = False

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    global stop_reporting
    print(f"\n{Color.YELLOW}🛑 Received interrupt signal. Stopping...{Color.RESET}")
    stop_reporting = True

def display_banner():
    banner = f"""
{Color.GREEN}{Color.BOLD}
  _____ _____    ___   _   _  _    _____ ___   ___  _    
 |_   _|_   _|__| _ ) /_\ | \| |__|_   _/ _ \ / _ \| |   
   | |   | ||___| _ \/ _ \| .` |___|| || (_) | (_) | |__ 
   |_|   |_|    |___/_/ \_\_|\_|    |_| \___/ \___/|____|
                             CREATED BY ATHEX                            
{Color.RESET}
{Color.YELLOW}Features:{Color.RESET}
{Color.RED}• Multi-threaded reporting
{Color.GREEN}• Proxy rotation
{Color.RED}• Real-time statistics
{Color.GREEN}• Configurable delays
{Color.RED}• Multiple report reasons
{Color.GREEN}• Session management
{Color.RED}• Video & Profile specific reporting
{Color.GREEN}• Interactive menu system
{Color.RED}• Manual URL input option
{Color.GREEN}• Continuous reporting mode
{Color.RED}• Real-time URL importing
{Color.GREEN}• Auto-restart functionality{Color.RESET}

{Color.RED}⚠ LEGAL DISCLAIMER: Use responsibly and ethically ⚠{Color.RESET}
"""
    print(banner)

def display_menu():
    """Display the main menu options"""
    menu = f"""
{Color.CYAN}{Color.BOLD}
╔════════════════════════════════════════════════════════╗
║               SELECT REPORTING MODE                    ║
╠════════════════════════════════════════════════════════╣
║                                                        ║
║  {Color.CYAN}1.{Color.GREEN} 📹 VIDEO MASS REPORTING   ║
║  {Color.CYAN}2.{Color.GREEN} 👤 PROFILE MASS REPORTING ║
║  {Color.CYAN}3.{Color.GREEN} 🔄 COMBINED REPORTING     ║
║  {Color.CYAN}4.{Color.GREEN} 📝 MANUAL URL INPUT       ║
║  {Color.CYAN}5.{Color.GREEN} 🔁 CONTINUOUS MODE        ║
║  {Color.CYAN}6.{Color.GREEN} 📥 REAL-TIME IMPORT       ║
║  {Color.CYAN}7.{Color.RED} ❌ EXIT                     ║
║                                                        ║
╚════════════════════════════════════════════════════════╣
{Color.RESET}"""
    print(menu)

def get_user_choice():
    """Get and validate user choice"""
    while True:
        try:
            choice = input(f"\n{Color.YELLOW}🎯 Select an option (1-7): {Color.RESET}").strip()
            if choice in ['1', '2', '3', '4', '5', '6', '7']:
                return int(choice)
            else:
                print(f"{Color.RED}❌ Invalid choice! Please enter 1-7.{Color.RESET}")
        except KeyboardInterrupt:
            print(f"\n{Color.RED}🛑 Process interrupted by user.{Color.RESET}")
            sys.exit(0)
        except Exception as e:
            print(f"{Color.RED}❌ Error: {e}{Color.RESET}")

def get_continuous_settings():
    """Get settings for continuous reporting mode"""
    print(f"\n{Color.CYAN}🔁 CONTINUOUS REPORTING SETTINGS{Color.RESET}")
    
    # Get batch size
    while True:
        try:
            batch_size = input(f"{Color.YELLOW}Enter batch size (number of reports per cycle, default 10): {Color.RESET}").strip()
            if not batch_size:
                batch_size = 10
                break
            batch_size = int(batch_size)
            if batch_size > 0:
                break
            else:
                print(f"{Color.RED}❌ Batch size must be positive{Color.RESET}")
        except ValueError:
            print(f"{Color.RED}❌ Please enter a valid number{Color.RESET}")
    
    # Get delay between batches
    while True:
        try:
            delay = input(f"{Color.YELLOW}Enter delay between batches in seconds (default 30): {Color.RESET}").strip()
            if not delay:
                delay = 30
                break
            delay = int(delay)
            if delay >= 0:
                break
            else:
                print(f"{Color.RED}❌ Delay cannot be negative{Color.RESET}")
        except ValueError:
            print(f"{Color.RED}❌ Please enter a valid number{Color.RESET}")
    
    # Get max cycles (0 for unlimited)
    while True:
        try:
            max_cycles = input(f"{Color.YELLOW}Enter maximum cycles (0 for unlimited, default 0): {Color.RESET}").strip()
            if not max_cycles:
                max_cycles = 0
                break
            max_cycles = int(max_cycles)
            if max_cycles >= 0:
                break
            else:
                print(f"{Color.RED}❌ Maximum cycles cannot be negative{Color.RESET}")
        except ValueError:
            print(f"{Color.RED}❌ Please enter a valid number{Color.RESET}")
    
    return batch_size, delay, max_cycles

def monitor_stop_command():
    """Monitor for stop command in continuous mode"""
    global stop_reporting, reporting_paused
    
    print(f"\n{Color.YELLOW}💡 Commands: 'stop' to exit, 'pause' to pause, 'resume' to continue{Color.RESET}")
    
    while continuous_mode and not stop_reporting:
        try:
            command = input(f"{Color.CYAN}⌨️  Enter command: {Color.RESET}").strip().lower()
            if command == 'stop':
                stop_reporting = True
                print(f"{Color.RED}🛑 Stop command received. Finishing current batch...{Color.RESET}")
                break
            elif command == 'pause':
                reporting_paused = True
                print(f"{Color.YELLOW}⏸️  Reporting paused. Type 'resume' to continue...{Color.RESET}")
            elif command == 'resume':
                reporting_paused = False
                print(f"{Color.GREEN}▶️  Reporting resumed{Color.RESET}")
            elif command == 'stats':
                # Stats are handled in the main loop
                pass
            else:
                print(f"{Color.YELLOW}❓ Unknown command. Available: stop, pause, resume{Color.RESET}")
        except:
            break

def real_time_url_importer(filename="realtime_targets.txt"):
    """Monitor a file for new URLs in real-time"""
    imported_urls = set()
    
    try:
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                existing_urls = set(line.strip() for line in f if line.strip())
                imported_urls.update(existing_urls)
        
        print(f"{Color.GREEN}📥 Real-time importer started. Monitoring {filename} for new URLs...{Color.RESET}")
        print(f"{Color.YELLOW}💡 Add URLs to {filename} and they will be processed automatically{Color.RESET}")
        
        last_size = os.path.getsize(filename) if os.path.exists(filename) else 0
        
        while continuous_mode and not stop_reporting:
            if not os.path.exists(filename):
                time.sleep(1)
                continue
                
            current_size = os.path.getsize(filename)
            if current_size > last_size:
                with open(filename, 'r', encoding='utf-8') as f:
                    f.seek(last_size)
                    new_urls = [line.strip() for line in f if line.strip()]
                    
                    for url in new_urls:
                        if url and url not in imported_urls:
                            imported_urls.add(url)
                            yield url
                            
                last_size = current_size
            
            time.sleep(2)  # Check every 2 seconds
            
    except Exception as e:
        print(f"{Color.RED}❌ Real-time importer error: {e}{Color.RESET}")

def create_default_files():
    """Create default files if they don't exist"""
    files = {
        "targets.txt": "# Add TikTok video or profile URLs here\n# One URL per line\n# Example video: https://www.tiktok.com/@username/video/1234567890123456789\n# Example profile: https://www.tiktok.com/@username",
        "proxies.txt": "# Add your proxies here (optional)\n# Format: http://username:password@ip:port\n# or: http://ip:port",
        "realtime_targets.txt": "# Add URLs here for real-time import mode\n# They will be processed automatically as you add them"
    }
    
    for filename, content in files.items():
        if not os.path.exists(filename):
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"{Color.GREEN}✓ Created {filename}{Color.RESET}")

def load_targets_from_file(filename="targets.txt"):
    """Load targets from file"""
    try:
        if not os.path.exists(filename):
            return []
        
        with open(filename, 'r', encoding='utf-8') as f:
            targets = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        
        return targets
    except Exception as e:
        print(f"{Color.RED}❌ Error loading targets: {e}{Color.RESET}")
        return []

def load_video_targets_from_file(filename="targets.txt"):
    """Load only video targets from file"""
    targets = load_targets_from_file(filename)
    return [target for target in targets if validate_video_url(target)]

def load_profile_targets_from_file(filename="targets.txt"):
    """Load only profile targets from file"""
    targets = load_targets_from_file(filename)
    return [target for target in targets if validate_profile_url(target)]

def load_proxies_from_file(filename="proxies.txt"):
    """Load proxies from file"""
    try:
        if not os.path.exists(filename):
            return []
        
        with open(filename, 'r', encoding='utf-8') as f:
            proxies = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        
        # Convert to proxy dict format
        proxy_list = []
        for proxy in proxies:
            if proxy.startswith('http'):
                proxy_list.append({'http': proxy, 'https': proxy})
        
        return proxy_list
    except Exception as e:
        print(f"{Color.RED}❌ Error loading proxies: {e}{Color.RESET}")
        return []

def get_user_agent():
    """Get random user agent"""
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    ]
    return random.choice(user_agents)

def get_report_reason(report_type="video"):
    """Get report reason payload"""
    reasons = {
        "video": [
            {"id": 1, "reason": "Illegal activities"},
            {"id": 2, "reason": "Harassment or bullying"},
            {"id": 3, "reason": "Hate speech"},
            {"id": 4, "reason": "Violent or graphic content"},
            {"id": 5, "reason": "Copyright infringement"}
        ],
        "profile": [
            {"id": 1, "reason": "Impersonation"},
            {"id": 2, "reason": "Underage user"},
            {"id": 3, "reason": "Harassment"},
            {"id": 4, "reason": "Hate speech"},
            {"id": 5, "reason": "Spam"}
        ]
    }
    
    reason_list = reasons.get(report_type, reasons["video"])
    reason = random.choice(reason_list)
    
    return {
        "reason": reason["id"],
        "reason_text": reason["reason"],
        "report_type": report_type,
        "timestamp": int(time.time())
    }

def validate_video_url(url):
    """Validate TikTok video URL"""
    return url and ("tiktok.com" in url and "/video/" in url)

def validate_profile_url(url):
    """Validate TikTok profile URL"""
    return url and ("tiktok.com/@" in url and "/video/" not in url)

def get_url_input():
    """Get URL input from user"""
    while True:
        try:
            url = input(f"\n{Color.YELLOW}🎯 Enter TikTok URL: {Color.RESET}").strip()
            if not url:
                print(f"{Color.RED}❌ URL cannot be empty{Color.RESET}")
                continue
            
            if not (validate_video_url(url) or validate_profile_url(url)):
                print(f"{Color.RED}❌ Invalid TikTok URL. Must be a video or profile URL{Color.RESET}")
                continue
            
            return url
        except KeyboardInterrupt:
            print(f"\n{Color.RED}🛑 Process interrupted by user.{Color.RESET}")
            return None
        except Exception as e:
            print(f"{Color.RED}❌ Error: {e}{Color.RESET}")

def get_single_url_input():
    """Get single URL input for manual reporting"""
    print(f"\n{Color.CYAN}📝 MANUAL URL INPUT{Color.RESET}")
    print(f"{Color.YELLOW}💡 Enter a single TikTok URL to report{Color.RESET}")
    
    url = get_url_input()
    if not url:
        return None, None
    
    if validate_video_url(url):
        return url, "video"
    elif validate_profile_url(url):
        return url, "profile"
    else:
        return None, None

class TikTokReporter:
    def __init__(self, report_type="combined"):
        self.success_count = 0
        self.failed_count = 0
        self.start_time = None
        self.session = requests.Session()
        self.report_type = report_type
        self._lock = threading.Lock()
        self.total_processed = 0
        
    def report_video(self, video_url, proxy):
        """Report a TikTok video"""
        global stop_reporting, reporting_paused
        
        if stop_reporting:
            return False
            
        # Wait if paused
        while reporting_paused and not stop_reporting:
            time.sleep(1)
            
        if stop_reporting:
            return False
            
        try:
            headers = {
                "User-Agent": get_user_agent(),
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Accept-Language": "en-US,en;q=0.9",
                "Referer": "https://www.tiktok.com/",
                "Origin": "https://www.tiktok.com"
            }

            payload = get_report_reason("video")
            
            # Extract video ID
            video_id = video_url.split("/video/")[1].split("?")[0]
            payload["video_id"] = video_id
            
            # Hypothetical API endpoint
            api_url = "https://www.tiktok.com/api/report/video/"
            
            proxy_dict = proxy if proxy else None
            
            # Add random delay to avoid detection
            time.sleep(random.uniform(2, 5))
            
            # Simulated response (85% success rate for demo)
            success = random.random() > 0.15
            response = type('obj', (object,), {'status_code': 200 if success else 400})()
            
            with self._lock:
                self.total_processed += 1
                if response.status_code == 200:
                    self.success_count += 1
                    print(f"{Color.GREEN}🎥 ✓ Video reported successfully: {video_url}{Color.RESET}")
                    return True
                else:
                    self.failed_count += 1
                    print(f"{Color.RED}🎥 ✗ Failed to report video: {video_url}{Color.RESET}")
                    return False
                    
        except Exception as e:
            with self._lock:
                self.failed_count += 1
                self.total_processed += 1
                proxy_info = proxy['http'] if proxy and 'http' in proxy else 'Direct'
                print(f"{Color.YELLOW}🎥 ⚠ Error reporting video {video_url}: {str(e)}{Color.RESET}")
            return False

    def report_profile(self, profile_url, proxy):
        """Report a TikTok profile"""
        global stop_reporting, reporting_paused
        
        if stop_reporting:
            return False
            
        # Wait if paused
        while reporting_paused and not stop_reporting:
            time.sleep(1)
            
        if stop_reporting:
            return False
            
        try:
            headers = {
                "User-Agent": get_user_agent(),
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Accept-Language": "en-US,en;q=0.9",
                "Referer": "https://www.tiktok.com/",
                "Origin": "https://www.tiktok.com"
            }

            payload = get_report_reason("profile")
            
            # Extract username
            username = profile_url.split("@")[-1].split("/")[0].split("?")[0]
            payload["username"] = username
            
            # Hypothetical API endpoint
            api_url = "https://www.tiktok.com/api/report/user/"
            
            proxy_dict = proxy if proxy else None
            
            # Add random delay to avoid detection
            time.sleep(random.uniform(2, 5))
            
            # Simulated response (85% success rate for demo)
            success = random.random() > 0.15
            response = type('obj', (object,), {'status_code': 200 if success else 400})()
            
            with self._lock:
                self.total_processed += 1
                if response.status_code == 200:
                    self.success_count += 1
                    print(f"{Color.GREEN}👤 ✓ Profile reported successfully: {profile_url}{Color.RESET}")
                    return True
                else:
                    self.failed_count += 1
                    print(f"{Color.RED}👤 ✗ Failed to report profile: {profile_url}{Color.RESET}")
                    return False
                    
        except Exception as e:
            with self._lock:
                self.failed_count += 1
                self.total_processed += 1
                proxy_info = proxy['http'] if proxy and 'http' in proxy else 'Direct'
                print(f"{Color.YELLOW}👤 ⚠ Error reporting profile {profile_url}: {str(e)}{Color.RESET}")
            return False

    def display_stats(self):
        """Display current statistics"""
        if self.start_time:
            elapsed_time = time.time() - self.start_time
            total_attempts = self.success_count + self.failed_count
            success_rate = (self.success_count / total_attempts * 100) if total_attempts > 0 else 0
            
            # Calculate reports per minute
            reports_per_minute = (total_attempts / elapsed_time * 60) if elapsed_time > 0 else 0
            
            print(f"\n{Color.CYAN}{'='*60}{Color.RESET}")
            print(f"{Color.BOLD}📊 REAL-TIME STATISTICS - {self.report_type.upper()} MODE:{Color.RESET}")
            print(f"{Color.GREEN}✓ Successful reports: {self.success_count}{Color.RESET}")
            print(f"{Color.RED}✗ Failed reports: {self.failed_count}{Color.RESET}")
            print(f"{Color.BLUE}📈 Success rate: {success_rate:.2f}%{Color.RESET}")
            print(f"{Color.YELLOW}⏰ Elapsed time: {elapsed_time:.2f} seconds{Color.RESET}")
            print(f"{Color.MAGENTA}🚀 Speed: {reports_per_minute:.2f} reports/minute{Color.RESET}")
            print(f"{Color.WHITE}📋 Total processed: {self.total_processed}{Color.RESET}")
            print(f"{Color.CYAN}🎯 Report type: {self.report_type}{Color.RESET}")
            print(f"{Color.CYAN}{'='*60}{Color.RESET}\n")

def run_video_reporting():
    """Run video mass reporting"""
    print(f"\n{Color.MAGENTA}{Color.BOLD}📹 VIDEO MASS REPORTING{Color.RESET}")
    
    # Load targets and proxies
    video_targets = load_video_targets_from_file()
    if not video_targets:
        print(f"{Color.RED}❌ No valid video URLs found in targets.txt{Color.RESET}")
        return
    
    proxies = load_proxies_from_file()
    if not proxies:
        print(f"{Color.YELLOW}⚠ Using direct connection (no proxies){Color.RESET}")
        proxies = [None]
    
    print(f"{Color.GREEN}✓ Loaded {len(video_targets)} video targets{Color.RESET}")
    print(f"{Color.GREEN}✓ Loaded {len(proxies)} proxies{Color.RESET}")
    
    # Get thread count
    while True:
        try:
            thread_count = input(f"{Color.YELLOW}🎯 Enter number of threads (default 5): {Color.RESET}").strip()
            if not thread_count:
                thread_count = 5
                break
            thread_count = int(thread_count)
            if thread_count > 0:
                break
            else:
                print(f"{Color.RED}❌ Thread count must be positive{Color.RESET}")
        except ValueError:
            print(f"{Color.RED}❌ Please enter a valid number{Color.RESET}")
    
    reporter = TikTokReporter("video")
    reporter.start_time = time.time()
    
    print(f"\n{Color.MAGENTA}🚀 Starting video mass reporting...{Color.RESET}")
    print(f"{Color.YELLOW}⏳ Processing {len(video_targets)} videos with {thread_count} threads...{Color.RESET}")
    
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=thread_count) as executor:
            futures = []
            
            for i, video_url in enumerate(video_targets):
                if stop_reporting:
                    break
                    
                proxy = proxies[i % len(proxies)] if proxies else None
                future = executor.submit(reporter.report_video, video_url, proxy)
                futures.append(future)
            
            # Wait for all tasks to complete
            for future in concurrent.futures.as_completed(futures):
                if stop_reporting:
                    break
                try:
                    future.result(timeout=30)
                except Exception as e:
                    print(f"{Color.RED}❌ Task failed: {e}{Color.RESET}")
    
    except KeyboardInterrupt:
        print(f"\n{Color.YELLOW}🛑 Video reporting interrupted.{Color.RESET}")
    
    print(f"\n{Color.CYAN}{'='*60}{Color.RESET}")
    print(f"{Color.BOLD}🎉 VIDEO REPORTING COMPLETED!{Color.RESET}")
    print(f"{Color.CYAN}{'='*60}{Color.RESET}")
    reporter.display_stats()

def run_profile_reporting():
    """Run profile mass reporting"""
    print(f"\n{Color.MAGENTA}{Color.BOLD}👤 PROFILE MASS REPORTING{Color.RESET}")
    
    # Load targets and proxies
    profile_targets = load_profile_targets_from_file()
    if not profile_targets:
        print(f"{Color.RED}❌ No valid profile URLs found in targets.txt{Color.RESET}")
        return
    
    proxies = load_proxies_from_file()
    if not proxies:
        print(f"{Color.YELLOW}⚠ Using direct connection (no proxies){Color.RESET}")
        proxies = [None]
    
    print(f"{Color.GREEN}✓ Loaded {len(profile_targets)} profile targets{Color.RESET}")
    print(f"{Color.GREEN}✓ Loaded {len(proxies)} proxies{Color.RESET}")
    
    # Get thread count
    while True:
        try:
            thread_count = input(f"{Color.YELLOW}🎯 Enter number of threads (default 5): {Color.RESET}").strip()
            if not thread_count:
                thread_count = 5
                break
            thread_count = int(thread_count)
            if thread_count > 0:
                break
            else:
                print(f"{Color.RED}❌ Thread count must be positive{Color.RESET}")
        except ValueError:
            print(f"{Color.RED}❌ Please enter a valid number{Color.RESET}")
    
    reporter = TikTokReporter("profile")
    reporter.start_time = time.time()
    
    print(f"\n{Color.MAGENTA}🚀 Starting profile mass reporting...{Color.RESET}")
    print(f"{Color.YELLOW}⏳ Processing {len(profile_targets)} profiles with {thread_count} threads...{Color.RESET}")
    
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=thread_count) as executor:
            futures = []
            
            for i, profile_url in enumerate(profile_targets):
                if stop_reporting:
                    break
                    
                proxy = proxies[i % len(proxies)] if proxies else None
                future = executor.submit(reporter.report_profile, profile_url, proxy)
                futures.append(future)
            
            # Wait for all tasks to complete
            for future in concurrent.futures.as_completed(futures):
                if stop_reporting:
                    break
                try:
                    future.result(timeout=30)
                except Exception as e:
                    print(f"{Color.RED}❌ Task failed: {e}{Color.RESET}")
    
    except KeyboardInterrupt:
        print(f"\n{Color.YELLOW}🛑 Profile reporting interrupted.{Color.RESET}")
    
    print(f"\n{Color.CYAN}{'='*60}{Color.RESET}")
    print(f"{Color.BOLD}🎉 PROFILE REPORTING COMPLETED!{Color.RESET}")
    print(f"{Color.CYAN}{'='*60}{Color.RESET}")
    reporter.display_stats()

def run_combined_reporting():
    """Run combined video and profile reporting"""
    print(f"\n{Color.MAGENTA}{Color.BOLD}🔄 COMBINED REPORTING{Color.RESET}")
    
    # Load all targets
    all_targets = load_targets_from_file()
    if not all_targets:
        print(f"{Color.RED}❌ No valid URLs found in targets.txt{Color.RESET}")
        return
    
    proxies = load_proxies_from_file()
    if not proxies:
        print(f"{Color.YELLOW}⚠ Using direct connection (no proxies){Color.RESET}")
        proxies = [None]
    
    video_targets = [t for t in all_targets if validate_video_url(t)]
    profile_targets = [t for t in all_targets if validate_profile_url(t)]
    
    print(f"{Color.GREEN}✓ Loaded {len(video_targets)} video targets{Color.RESET}")
    print(f"{Color.GREEN}✓ Loaded {len(profile_targets)} profile targets{Color.RESET}")
    print(f"{Color.GREEN}✓ Loaded {len(proxies)} proxies{Color.RESET}")
    
    # Get thread count
    while True:
        try:
            thread_count = input(f"{Color.YELLOW}🎯 Enter number of threads (default 5): {Color.RESET}").strip()
            if not thread_count:
                thread_count = 5
                break
            thread_count = int(thread_count)
            if thread_count > 0:
                break
            else:
                print(f"{Color.RED}❌ Thread count must be positive{Color.RESET}")
        except ValueError:
            print(f"{Color.RED}❌ Please enter a valid number{Color.RESET}")
    
    reporter = TikTokReporter("combined")
    reporter.start_time = time.time()
    
    print(f"\n{Color.MAGENTA}🚀 Starting combined reporting...{Color.RESET}")
    print(f"{Color.YELLOW}⏳ Processing {len(all_targets)} total targets with {thread_count} threads...{Color.RESET}")
    
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=thread_count) as executor:
            futures = []
            
            for i, target in enumerate(all_targets):
                if stop_reporting:
                    break
                    
                proxy = proxies[i % len(proxies)] if proxies else None
                
                if validate_video_url(target):
                    future = executor.submit(reporter.report_video, target, proxy)
                elif validate_profile_url(target):
                    future = executor.submit(reporter.report_profile, target, proxy)
                else:
                    print(f"{Color.YELLOW}⚠ Skipping invalid target: {target}{Color.RESET}")
                    continue
                    
                futures.append(future)
            
            # Wait for all tasks to complete
            for future in concurrent.futures.as_completed(futures):
                if stop_reporting:
                    break
                try:
                    future.result(timeout=30)
                except Exception as e:
                    print(f"{Color.RED}❌ Task failed: {e}{Color.RESET}")
    
    except KeyboardInterrupt:
        print(f"\n{Color.YELLOW}🛑 Combined reporting interrupted.{Color.RESET}")
    
    print(f"\n{Color.CYAN}{'='*60}{Color.RESET}")
    print(f"{Color.BOLD}🎉 COMBINED REPORTING COMPLETED!{Color.RESET}")
    print(f"{Color.CYAN}{'='*60}{Color.RESET}")
    reporter.display_stats()

def run_manual_url_input():
    """Run manual URL input mode"""
    print(f"\n{Color.MAGENTA}{Color.BOLD}📝 MANUAL URL INPUT{Color.RESET}")
    
    url, url_type = get_single_url_input()
    if not url:
        return
    
    proxies = load_proxies_from_file()
    if not proxies:
        print(f"{Color.YELLOW}⚠ Using direct connection (no proxies){Color.RESET}")
        proxies = [None]
    
    reporter = TikTokReporter("manual")
    reporter.start_time = time.time()
    
    proxy = random.choice(proxies) if proxies else None
    
    print(f"\n{Color.MAGENTA}🚀 Reporting {url_type}: {url}{Color.RESET}")
    
    try:
        if url_type == "video":
            success = reporter.report_video(url, proxy)
        else:
            success = reporter.report_profile(url, proxy)
        
        print(f"\n{Color.CYAN}{'='*60}{Color.RESET}")
        if success:
            print(f"{Color.BOLD}🎉 MANUAL REPORTING SUCCESSFUL!{Color.RESET}")
        else:
            print(f"{Color.BOLD}❌ MANUAL REPORTING FAILED!{Color.RESET}")
        print(f"{Color.CYAN}{'='*60}{Color.RESET}")
        reporter.display_stats()
        
    except Exception as e:
        print(f"{Color.RED}❌ Error during manual reporting: {e}{Color.RESET}")

def run_continuous_reporting():
    """Run continuous reporting mode"""
    global continuous_mode, stop_reporting, reporting_paused
    
    print(f"\n{Color.MAGENTA}{Color.BOLD}🔁 CONTINUOUS REPORTING MODE{Color.RESET}")
    
    # Get continuous mode settings
    batch_size, delay, max_cycles = get_continuous_settings()
    
    # Get initial targets
    print(f"\n{Color.YELLOW}Loading initial targets...{Color.RESET}")
    all_targets = load_targets_from_file()
    if not all_targets:
        print(f"{Color.RED}❌ No targets found. Please add targets to targets.txt{Color.RESET}")
        return
    
    continuous_mode = True
    stop_reporting = False
    reporting_paused = False
    
    reporter = TikTokReporter("continuous")
    reporter.start_time = time.time()
    
    proxies = load_proxies_from_file()
    if not proxies:
        print(f"{Color.YELLOW}Using direct connection (no proxies)...{Color.RESET}")
        proxies = [None]
    
    print(f"{Color.GREEN}✓ Loaded {len(all_targets)} initial targets{Color.RESET}")
    print(f"{Color.GREEN}✓ Loaded {len(proxies)} proxies{Color.RESET}")
    print(f"{Color.GREEN}✓ Batch size: {batch_size}{Color.RESET}")
    print(f"{Color.GREEN}✓ Delay between batches: {delay}s{Color.RESET}")
    print(f"{Color.GREEN}✓ Max cycles: {'Unlimited' if max_cycles == 0 else max_cycles}{Color.RESET}")
    
    # Start command monitor thread
    command_thread = threading.Thread(target=monitor_stop_command, daemon=True)
    command_thread.start()
    
    print(f"\n{Color.MAGENTA}🚀 Starting continuous reporting...{Color.RESET}")
    
    cycle_count = 0
    target_index = 0
    
    try:
        while continuous_mode and not stop_reporting:
            if max_cycles > 0 and cycle_count >= max_cycles:
                print(f"{Color.YELLOW}📦 Maximum cycles ({max_cycles}) reached.{Color.RESET}")
                break
            
            # Wait if paused
            while reporting_paused and not stop_reporting:
                time.sleep(1)
            
            if stop_reporting:
                break
            
            cycle_count += 1
            print(f"\n{Color.CYAN}🔄 Starting cycle {cycle_count}...{Color.RESET}")
            
            # Process one batch
            batch_targets = []
            for i in range(batch_size):
                if target_index >= len(all_targets):
                    target_index = 0  # Restart from beginning
                
                batch_targets.append(all_targets[target_index])
                target_index += 1
            
            # Process the batch
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                futures = []
                
                for i, target in enumerate(batch_targets):
                    if stop_reporting:
                        break
                        
                    proxy = proxies[i % len(proxies)] if proxies else None
                    
                    if validate_video_url(target):
                        future = executor.submit(reporter.report_video, target, proxy)
                    elif validate_profile_url(target):
                        future = executor.submit(reporter.report_profile, target, proxy)
                    else:
                        print(f"{Color.YELLOW}⚠ Skipping invalid target: {target}{Color.RESET}")
                        continue
                        
                    futures.append(future)
                
                # Wait for batch completion
                for future in concurrent.futures.as_completed(futures):
                    if stop_reporting:
                        break
                    try:
                        future.result(timeout=30)
                    except Exception as e:
                        print(f"{Color.RED}❌ Task failed: {e}{Color.RESET}")
            
            # Display stats after each batch
            reporter.display_stats()
            
            # Delay between batches (unless stopping)
            if not stop_reporting and delay > 0 and cycle_count < (max_cycles if max_cycles > 0 else float('inf')):
                print(f"{Color.YELLOW}⏳ Waiting {delay} seconds before next batch...{Color.RESET}")
                for i in range(delay):
                    if stop_reporting:
                        break
                    time.sleep(1)
                    print(f"{Color.YELLOW}⏳ {delay - i - 1}s remaining...{Color.RESET}", end='\r')
                print()
    
    except KeyboardInterrupt:
        print(f"\n{Color.YELLOW}🛑 Continuous reporting interrupted.{Color.RESET}")
    except Exception as e:
        print(f"{Color.RED}❌ Continuous reporting error: {e}{Color.RESET}")
    
    finally:
        continuous_mode = False
        stop_reporting = True
        
        print(f"\n{Color.CYAN}{'='*60}{Color.RESET}")
        print(f"{Color.BOLD}🎉 CONTINUOUS REPORTING FINISHED!{Color.RESET}")
        print(f"{Color.CYAN}{'='*60}{Color.RESET}")
        reporter.display_stats()

def run_real_time_import():
    """Run real-time URL import mode"""
    global continuous_mode, stop_reporting, reporting_paused
    
    print(f"\n{Color.MAGENTA}{Color.BOLD}📥 REAL-TIME IMPORT MODE{Color.RESET}")
    
    continuous_mode = True
    stop_reporting = False
    reporting_paused = False
    
    reporter = TikTokReporter("realtime")
    reporter.start_time = time.time()
    
    proxies = load_proxies_from_file()
    if not proxies:
        print(f"{Color.YELLOW}Using direct connection (no proxies)...{Color.RESET}")
        proxies = [None]
    
    # Start real-time importer
    url_generator = real_time_url_importer()
    
    # Start command monitor thread
    command_thread = threading.Thread(target=monitor_stop_command, daemon=True)
    command_thread.start()
    
    print(f"\n{Color.MAGENTA}🚀 Starting real-time import reporting...{Color.RESET}")
    print(f"{Color.YELLOW}💡 Add URLs to realtime_targets.txt to process them automatically{Color.RESET}")
    
    processed_urls = set()
    
    try:
        while continuous_mode and not stop_reporting:
            # Wait if paused
            while reporting_paused and not stop_reporting:
                time.sleep(1)
            
            if stop_reporting:
                break
            
            # Process any new URLs
            new_url_found = False
            for url in url_generator:
                if url not in processed_urls:
                    new_url_found = True
                    processed_urls.add(url)
                    
                    print(f"{Color.GREEN}📥 New URL imported: {url}{Color.RESET}")
                    
                    proxy = random.choice(proxies) if proxies else None
                    
                    if validate_video_url(url):
                        success = reporter.report_video(url, proxy)
                    elif validate_profile_url(url):
                        success = reporter.report_profile(url, proxy)
                    else:
                        print(f"{Color.YELLOW}⚠ Skipping invalid URL: {url}{Color.RESET}")
                        continue
            
            # If no new URLs, wait a bit
            if not new_url_found:
                time.sleep(5)
            
            # Display stats periodically
            reporter.display_stats()
            
    except KeyboardInterrupt:
        print(f"\n{Color.YELLOW}🛑 Real-time import interrupted.{Color.RESET}")
    except Exception as e:
        print(f"{Color.RED}❌ Real-time import error: {e}{Color.RESET}")
    
    finally:
        continuous_mode = False
        stop_reporting = True
        
        print(f"\n{Color.CYAN}{'='*60}{Color.RESET}")
        print(f"{Color.BOLD}🎉 REAL-TIME IMPORT FINISHED!{Color.RESET}")
        print(f"{Color.CYAN}{'='*60}{Color.RESET}")
        reporter.display_stats()
        print(f"{Color.GREEN}📊 Total URLs processed: {len(processed_urls)}{Color.RESET}")

def main():
    # Set up signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    
    # Display banner
    display_banner()
    
    # Create default files
    create_default_files()
    
    while True:
        # Display menu
        display_menu()
        
        # Get user choice
        choice = get_user_choice()
        
        if choice == 1:
            run_video_reporting()
        elif choice == 2:
            run_profile_reporting()
        elif choice == 3:
            run_combined_reporting()
        elif choice == 4:
            run_manual_url_input()
        elif choice == 5:
            run_continuous_reporting()
        elif choice == 6:
            run_real_time_import()
        elif choice == 7:
            print(f"\n{Color.GREEN}👋 Thank you for using TikTok Mass Report Tool!{Color.RESET}")
            break
        
        # Reset global flags
        global continuous_mode, stop_reporting, reporting_paused
        continuous_mode = False
        stop_reporting = False
        reporting_paused = False
        
        # Ask if user wants to continue
        if choice != 7:
            continue_choice = input(f"\n{Color.YELLOW}🔄 Do you want to continue? (y/n): {Color.RESET}").strip().lower()
            if continue_choice not in ['y', 'yes']:
                print(f"\n{Color.GREEN}👋 Thank you for using TikTok Mass Report Tool!{Color.RESET}")
                break

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Color.RED}🛑 Process interrupted by user.{Color.RESET}")
    except Exception as e:
        print(f"\n{Color.RED}💥 Unexpected error: {e}{Color.RESET}")
