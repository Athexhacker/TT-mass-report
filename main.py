import requests
import re
import time
import json
from urllib.parse import urlparse, parse_qs

def print_colored_text(text, color_code):
    print(f"{color_code}{text}\033[0m")

def extract_video_id_from_url(url):
    """
    Extract video ID from various TikTok URL formats
    """
    # Clean the URL
    url = url.strip().split('?')[0]
    
    # Pattern 1: Direct video ID in path - https://www.tiktok.com/@username/video/1234567890123456789
    video_pattern1 = r'tiktok\.com\/@[\w\.-]+\/video\/(\d+)'
    match1 = re.search(video_pattern1, url)
    if match1:
        return match1.group(1)
    
    # Pattern 2: Short URL - https://vm.tiktok.com/abc123/
    short_pattern = r'vm\.tiktok\.com\/([\w]+)'
    match2 = re.search(short_pattern, url)
    if match2:
        return match2.group(1)
    
    # Pattern 3: Mobile URL - https://vt.tiktok.com/abc123/
    vt_pattern = r'vt\.tiktok\.com\/([\w]+)'
    match3 = re.search(vt_pattern, url)
    if match3:
        return match3.group(1)
    
    # Pattern 4: Direct video ID - just numbers
    if url.isdigit() and len(url) > 15:
        return url
    
    return None

def get_video_info(video_id):
    """
    Get video information using TikTok API
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.tiktok.com/',
        }
        
        # Try multiple API endpoints to get video info
        api_urls = [
            f"https://www.tiktok.com/node/share/video/{video_id}",
            f"https://api.tiktok.com/aweme/v1/aweme/detail/?aweme_id={video_id}",
            f"https://www.tiktok.com/api/item/detail/?itemId={video_id}"
        ]
        
        for api_url in api_urls:
            try:
                response = requests.get(api_url, headers=headers, timeout=10)
                if response.status_code == 200:
                    return response.json()
            except:
                continue
        
        return None
    except Exception as e:
        return None

def generate_report_url(video_id):
    """
    Generate report URL from video ID
    """
    report_urls = [
        f"https://www.tiktok.com/api/report/item/?itemId={video_id}",
        f"https://www.tiktok.com/aweme/v1/aweme/report/?aweme_id={video_id}",
        f"https://api.tiktok.com/aweme/v1/aweme/report/?aweme_id={video_id}",
        f"https://www.tiktok.com/node/share/video/{video_id}/report"
    ]
    return report_urls[0]  # Return the most common one

def validate_tiktok_url(url):
    """
    Check if the URL is a valid TikTok URL
    """
    tiktok_domains = [
        'tiktok.com', 'www.tiktok.com', 'vm.tiktok.com', 
        'vt.tiktok.com', 'm.tiktok.com', 'api.tiktok.com'
    ]
    
    try:
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.lower()
        
        # Check if domain is TikTok
        for tiktok_domain in tiktok_domains:
            if domain == tiktok_domain or domain.endswith('.' + tiktok_domain):
                return True
                
        # Check if it's just a video ID (numbers only)
        if url.isdigit() and len(url) > 15:
            return True
            
        return False
    except:
        return False

def main():
    green_color = "\033[92m"
    blue_color = "\033[94m"
    red_color = "\033[91m"
    yellow_color = "\033[93m"
    cyan_color = "\033[96m"
    reset_color = "\033[0m"

    # Print big colored text
    big_text = """ 
_____ _____ ____                       _
|_   _|_   _|  _ \ ___ _ __   ___  _ __| |_
  | |   | | | |_) / _ \ '_ \ / _ \| '__| __|
  | |   | | |  _ <  __/ |_) | (_) | |  | |_
  |_|   |_| |_| \_\___| .__/ \___/|_|   \__|
  Created By ATHEX    |_| 
 (FucK Fake Accounts)

"""
    print_colored_text(big_text, green_color)
    
    print_colored_text("?? ENHANCED TIKTOK REPORT BOT", cyan_color)
    print_colored_text("Supports ALL TikTok URL formats:", yellow_color)
    print_colored_text("https://www.tiktok.com/@username/video/1234567890123456789", blue_color)
    print_colored_text("https://vm.tiktok.com/abc123/", blue_color)
    print_colored_text("https://vt.tiktok.com/abc123/", blue_color)
    print_colored_text("Direct Video ID: 1234567890123456789", blue_color)
    print_colored_text("Mobile links, Short links, etc.", blue_color)
    print_colored_text("="*60, cyan_color)

    report_count = 0

    while True:
        print_colored_text("\n?? Enter TikTok Video URL or Video ID:", green_color)
        user_input = input().strip()
        
        if user_input.lower() in ['exit', 'quit', 'stop']:
            break
            
        if not user_input:
            print_colored_text("? Please enter a valid URL or Video ID", red_color)
            continue

        # Validate if it's a TikTok URL or video ID
        if not validate_tiktok_url(user_input):
            print_colored_text("? Invalid TikTok URL or Video ID", red_color)
            print_colored_text("?? Supported formats:", yellow_color)
            print_colored_text("  - Regular: https://www.tiktok.com/@user/video/1234567890123456789", blue_color)
            print_colored_text("  - Short: https://vm.tiktok.com/abc123/", blue_color)
            print_colored_text("  - Mobile: https://vt.tiktok.com/abc123/", blue_color)
            print_colored_text("  - Direct ID: 1234567890123456789", blue_color)
            continue

        # Extract video ID
        print_colored_text("?? Extracting Video ID...", yellow_color)
        video_id = extract_video_id_from_url(user_input)
        
        if not video_id:
            print_colored_text("? Could not extract Video ID from URL", red_color)
            continue

        print_colored_text(f"? Video ID found: {video_id}", green_color)

        # Get video info to verify
        print_colored_text("?? Fetching video information...", yellow_color)
        video_info = get_video_info(video_id)
        
        if video_info:
            print_colored_text("? Video information retrieved successfully", green_color)
        else:
            print_colored_text("?? Could not fetch video info, but will try to report anyway", yellow_color)

        # Generate report URL
        report_url = generate_report_url(video_id)
        print_colored_text(f"?? Generated Report URL: {report_url}", cyan_color)

        # Ask for confirmation
        print_colored_text(f"\n?? Ready to start reporting Video ID: {video_id}", green_color)
        confirm = input("Start reporting? (y/n): ").lower().strip()
        if confirm not in ['y', 'yes']:
            continue

        print_colored_text("?? Starting automated reports...", green_color)
        
        report_session_count = 0
        max_reports_per_session = 50  # Safety limit
        
        try:
            while report_session_count < max_reports_per_session:
                try:
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                        'Accept': 'application/json, text/plain, */*',
                        'Accept-Language': 'en-US,en;q=0.9',
                        'Referer': f'https://www.tiktok.com/@user/video/{video_id}',
                        'Origin': 'https://www.tiktok.com',
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                    
                    # Add random delay to avoid detection
                    delay = 1 + (report_session_count % 3)  # 1-3 seconds
                    time.sleep(delay)
                    
                    response = requests.post(report_url, headers=headers, timeout=10)
                    report_count += 1
                    report_session_count += 1
                    
                    # Check response
                    if response.status_code == 200:
                        print_colored_text(f"? Report #{report_count} successful | Session: {report_session_count}", green_color)
                    elif response.status_code == 400:
                        print_colored_text(f"? Report #{report_count} failed - Bad Request", red_color)
                    elif response.status_code == 403:
                        print_colored_text(f"? Report #{report_count} failed - Access Denied", red_color)
                        break
                    elif response.status_code == 404:
                        print_colored_text(f"? Report #{report_count} failed - Video Not Found", red_color)
                        break
                    elif response.status_code == 429:
                        print_colored_text(f"?? Report #{report_count} - Rate Limited, waiting 30 seconds...", yellow_color)
                        time.sleep(30)
                    else:
                        print_colored_text(f"? Report #{report_count} failed - Status: {response.status_code}", red_color)
                        
                except requests.exceptions.Timeout:
                    print_colored_text(f"? Report #{report_count} - Timeout", yellow_color)
                except requests.exceptions.ConnectionError:
                    print_colored_text(f"?? Report #{report_count} - Connection Error", red_color)
                    break
                except requests.exceptions.RequestException as e:
                    print_colored_text(f"? Report #{report_count} - Error: {e}", red_color)
                    break
                except KeyboardInterrupt:
                    print_colored_text(f"\n?? Session interrupted by user", yellow_color)
                    break
                    
        except Exception as e:
            print_colored_text(f"?? Unexpected error: {e}", red_color)

        # Session summary
        print_colored_text(f"\n?? Session Complete:", cyan_color)
        print_colored_text(f"?? Video ID: {video_id}", blue_color)
        print_colored_text(f"?? Reports this session: {report_session_count}", blue_color)
        print_colored_text(f"?? Total overall reports: {report_count}", blue_color)

        # Continue or exit
        print_colored_text(f"\n?? Do you want to report another video?", green_color)
        continue_choice = input("Continue? (y/n): ").lower().strip()
        if continue_choice not in ['y', 'yes']:
            print_colored_text(f"\n?? Final statistics:", cyan_color)
            print_colored_text(f"?? Total reports sent: {report_count}", green_color)
            print_colored_text("?? Thank you for using Enhanced TikTok Report Bot!", green_color)
            break

if __name__ == "__main__":
    main()