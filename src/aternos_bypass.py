import os
import time
import logging
import json
import requests
import re
from datetime import datetime
from urllib.parse import urlparse, parse_qs

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('aternos_bypass.log')
    ]
)
logger = logging.getLogger(__name__)

class AternosBypassKeeper:
    """
    Bypasses Cloudflare using requests/session instead of Selenium
    """
    
    def __init__(self):
        self.username = os.getenv('ATERNOS_USERNAME', '_CRAFTEEE_')
        self.password = os.getenv('ATERNOS_PASSWORD', 'Albin4242')
        self.server = os.getenv('ATERNOS_SERVER', 'gameplannet.aternos.me:43658')
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
        })
        
        self.total_clicks = 0
        self.consecutive_fails = 0
        self.max_fails = 5
        
        logger.info("=" * 60)
        logger.info("🎮 ATORNOS BYPASS KEEPER")
        logger.info(f"👤 Username: {self.username}")
        logger.info("🛡️ Bypasses Cloudflare protection")
        logger.info("🎯 Strategy: API-based approach")
        logger.info("=" * 60)
    
    def get_auth_token(self):
        """Get Aternos auth token"""
        try:
            logger.info("🔑 Getting auth token...")
            
            # Get login page
            response = self.session.get('https://aternos.org/')
            time.sleep(2)
            
            # Look for auth token in page
            page_content = response.text
            
            # Try to find token in JavaScript
            token_patterns = [
                r'"token":"([^"]+)"',
                r"token:\s*'([^']+)'",
                r'ATERNOS_TOKEN\s*=\s*["\']([^"\']+)["\']',
                r'csrf-token["\']?\s*content=["\']([^"\']+)["\']',
            ]
            
            for pattern in token_patterns:
                match = re.search(pattern, page_content)
                if match:
                    token = match.group(1)
                    logger.info(f"✅ Found auth token: {token[:20]}...")
                    return token
            
            logger.warning("⚠️ No auth token found, trying alternative...")
            
            # Try to get token from cookies
            if 'ATERNOS_SESSION' in self.session.cookies:
                logger.info("✅ Using session cookie")
                return self.session.cookies.get('ATERNOS_SESSION')
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Token error: {e}")
            return None
    
    def login_with_api(self):
        """Login using Aternos API"""
        try:
            logger.info(f"🔐 Logging in as {self.username}...")
            
            # First, get the main page to set cookies
            self.session.get('https://aternos.org/')
            time.sleep(2)
            
            # Try to find login endpoint
            login_url = 'https://aternos.org/panel/ajax/account/login.php'
            
            # Prepare login data
            login_data = {
                'user': self.username,
                'password': self.password,
                'ajax': '1'
            }
            
            # Set headers for AJAX request
            headers = {
                'X-Requested-With': 'XMLHttpRequest',
                'Referer': 'https://aternos.org/',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'Origin': 'https://aternos.org',
            }
            
            # Try login
            response = self.session.post(login_url, data=login_data, headers=headers)
            time.sleep(2)
            
            # Check response
            if response.status_code == 200:
                try:
                    result = response.json()
                    if result.get('success') or 'redirect' in response.text.lower():
                        logger.info("🎉 Login successful via API!")
                        return True
                except:
                    if 'success' in response.text.lower() or 'logged' in response.text.lower():
                        logger.info("✅ Login appears successful")
                        return True
            
            # Try alternative login method
            logger.info("🔄 Trying alternative login method...")
            
            # Try to get session by visiting account page
            account_response = self.session.get('https://aternos.org/account/')
            time.sleep(2)
            
            # Check if we're logged in
            if self.username.lower() in account_response.text.lower():
                logger.info("✅ Logged in (username found on page)")
                return True
            
            # Check cookies
            if self.session.cookies.get('ATERNOS_SESSION'):
                logger.info("✅ Session cookie found")
                return True
            
            logger.error("❌ Login failed")
            return False
            
        except Exception as e:
            logger.error(f"❌ Login error: {e}")
            return False
    
    def get_server_status(self):
        """Get server status via API"""
        try:
            # Try to get server info
            response = self.session.get('https://aternos.org/server/')
            time.sleep(1)
            
            # Look for server status in page
            page_text = response.text.lower()
            
            if 'online' in page_text:
                logger.info("📊 Server: Online")
                return 'online'
            elif 'offline' in page_text:
                logger.info("📊 Server: Offline")
                return 'offline'
            elif 'starting' in page_text:
                logger.info("📊 Server: Starting")
                return 'starting'
            
            return 'unknown'
            
        except Exception as e:
            logger.error(f"❌ Status error: {e}")
            return 'error'
    
    def check_boost_button(self):
        """Check if boost button is available"""
        try:
            # Get server page
            response = self.session.get('https://aternos.org/server/')
            time.sleep(1)
            
            # Look for boost button
            page_text = response.text
            
            boost_indicators = [
                '+1</button>',
                'Get your free RAM boost',
                'data-action="boost"',
                'id="boost-button"',
                'class="boost-button"',
                'boost your server',
            ]
            
            for indicator in boost_indicators:
                if indicator in page_text:
                    logger.info("🎯 Boost button available")
                    return True
            
            # Also check for timer
            timer_patterns = [
                r'0:5[0-9]',
                r'0:[0-5][0-9]',
                r'1:0[0-9]',
            ]
            
            for pattern in timer_patterns:
                if re.search(pattern, page_text):
                    timer = re.search(pattern, page_text).group()
                    logger.info(f"⏰ Timer found: {timer}")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Boost check error: {e}")
            return False
    
    def click_boost_via_api(self):
        """Click boost button via API"""
        try:
            logger.info("⚡ Attempting to click boost via API...")
            
            # Try different API endpoints
            boost_endpoints = [
                'https://aternos.org/panel/ajax/server/boost.php',
                'https://aternos.org/server/ajax/boost.php',
                'https://aternos.org/ajax/boost.php',
            ]
            
            headers = {
                'X-Requested-With': 'XMLHttpRequest',
                'Referer': 'https://aternos.org/server/',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            }
            
            for endpoint in boost_endpoints:
                try:
                    response = self.session.post(endpoint, data={'ajax': '1'}, headers=headers)
                    time.sleep(1)
                    
                    if response.status_code == 200:
                        if 'success' in response.text.lower() or 'boost' in response.text.lower():
                            self.total_clicks += 1
                            self.consecutive_fails = 0
                            logger.info(f"✅ Boost clicked via API! Total: {self.total_clicks}")
                            return True
                except:
                    continue
            
            # Try form submission method
            logger.info("🔄 Trying form submission...")
            
            # Get the server page to find form
            response = self.session.get('https://aternos.org/server/')
            
            # Look for form
            if 'form' in response.text:
                # Try to find boost form
                form_pattern = r'<form[^>]*action="([^"]*boost[^"]*)"[^>]*>'
                match = re.search(form_pattern, response.text, re.IGNORECASE)
                
                if match:
                    form_action = match.group(1)
                    if not form_action.startswith('http'):
                        form_action = 'https://aternos.org' + form_action
                    
                    # Submit form
                    form_response = self.session.post(form_action)
                    if form_response.status_code == 200:
                        self.total_clicks += 1
                        logger.info(f"✅ Boost via form! Total: {self.total_clicks}")
                        return True
            
            logger.warning("⚠️ Could not click boost via API")
            return False
            
        except Exception as e:
            logger.error(f"❌ Boost click error: {e}")
            self.consecutive_fails += 1
            return False
    
    def keep_alive_simple(self):
        """Simple keep-alive by visiting page"""
        try:
            response = self.session.get('https://aternos.org/server/')
            logger.info("💓 Keep-alive ping sent")
            return response.status_code == 200
        except:
            return False
    
    def monitor(self):
        """Main monitoring loop"""
        logger.info("🚀 Starting bypass monitoring...")
        
        # First login
        if not self.login_with_api():
            logger.error("❌ Initial login failed")
            return False
        
        check_count = 0
        
        while self.consecutive_fails < self.max_fails:
            check_count += 1
            elapsed_minutes = (datetime.now() - datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)).seconds / 60
            
            # Log status
            if check_count % 3 == 0:
                logger.info(f"\n{'='*40}")
                logger.info(f"🔄 Check #{check_count}")
                logger.info(f"🎯 Total clicks: {self.total_clicks}")
                logger.info(f"❌ Consecutive fails: {self.consecutive_fails}")
                logger.info(f"{'='*40}")
            
            # Check server status
            status = self.get_server_status()
            
            if status == 'offline':
                logger.info("🔌 Server offline, waiting...")
                time.sleep(60)
                continue
            
            # Check for boost button
            if self.check_boost_button():
                logger.info("🎯 Boost button detected, attempting click...")
                if self.click_boost_via_api():
                    time.sleep(30)  # Wait after successful click
                else:
                    time.sleep(15)
            else:
                logger.info("⏳ No boost available, keeping alive...")
                self.keep_alive_simple()
                time.sleep(45)  # Check every 45 seconds
            
            # Re-login every 10 checks
            if check_count % 10 == 0:
                logger.info("🔄 Refreshing session...")
                self.login_with_api()
        
        logger.error(f"❌ Too many fails ({self.consecutive_fails})")
        return False
    
    def run(self):
        """Main run method"""
        try:
            return self.monitor()
        except KeyboardInterrupt:
            logger.info("👋 Stopped by user")
            return True
        except Exception as e:
            logger.error(f"❌ Fatal error: {e}")
            return False


if __name__ == "__main__":
    keeper = AternosBypassKeeper()
    keeper.run()
