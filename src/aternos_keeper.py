import os
import time
import logging
import random
import re
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('aternos_keeper.log')
    ]
)
logger = logging.getLogger(__name__)

class Aternos24_7Keeper:
    """
    Fixed Aternos 24/7 Server Keeper with updated login selectors
    """
    
    def __init__(self):
        """Initialize with environment variables"""
        self.username = os.getenv('ATERNOS_USERNAME', '_CRAFTEEE_')
        self.password = os.getenv('ATERNOS_PASSWORD', 'Albin4242')
        self.server_url = os.getenv('ATERNOS_SERVER', 'gameplannet.aternos.me:43658')
        
        # Configuration
        self.driver = None
        self.session_start = datetime.now()
        self.total_clicks = 0
        self.consecutive_fails = 0
        self.max_fails = 10
        self.is_running = False
        
        logger.info("=" * 60)
        logger.info("🎮 ATORNOS 24/7 SERVER KEEPER v2.0")
        logger.info(f"👤 Username: {self.username}")
        logger.info(f"🌐 Server: {self.server_url}")
        logger.info("🎯 Strategy: Click +1 button at 0:59")
        logger.info("=" * 60)
    
    def setup_driver(self):
        """Setup Chrome driver for Render"""
        try:
            logger.info("🚀 Setting up Chrome driver...")
            
            options = ChromeOptions()
            
            # Basic arguments
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--window-size=1920,1080')
            
            # For Chromium on Render
            options.binary_location = '/usr/bin/chromium-browser'
            
            # User agent
            options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            
            # Create driver
            self.driver = webdriver.Chrome(options=options)
            
            # Anti-detection
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            logger.info("✅ Chrome driver initialized")
            return True
            
        except Exception as e:
            logger.error(f"❌ Driver setup failed: {e}")
            return False
    
    def login(self):
        """Login to Aternos with UPDATED selectors"""
        try:
            logger.info(f"🔐 Logging in as {self.username}...")
            
            # Go to Aternos login page directly
            self.driver.get("https://aternos.org/account/")
            time.sleep(3)
            
            # Take screenshot to see what we're looking at
            self.driver.save_screenshot("login_page.png")
            logger.info("📸 Screenshot saved: login_page.png")
            
            # NEW: Aternos might have changed their form
            # Try multiple username field selectors
            username_selectors = [
                (By.ID, "user"),  # Old selector
                (By.NAME, "user"),  # Name attribute
                (By.CSS_SELECTOR, "input[type='text']"),  # Text input
                (By.CSS_SELECTOR, "input[placeholder*='username' i]"),  # Placeholder
                (By.CSS_SELECTOR, "input[placeholder*='user' i]"),
                (By.CSS_SELECTOR, "input[name*='user' i]"),
                (By.XPATH, "//input[@type='text' or @type='email']"),  # Any text input
                (By.XPATH, "//input[contains(@id, 'user') or contains(@name, 'user')]"),
            ]
            
            username_field = None
            for by, selector in username_selectors:
                try:
                    username_field = self.driver.find_element(by, selector)
                    if username_field:
                        logger.info(f"✅ Found username field with {by}: {selector}")
                        break
                except:
                    continue
            
            if not username_field:
                logger.error("❌ Could not find username field")
                # Try to see what's on the page
                page_html = self.driver.page_source[:1000]
                logger.info(f"📄 Page snippet: {page_html}")
                return False
            
            # Enter username
            username_field.clear()
            username_field.send_keys(self.username)
            logger.info("✅ Username entered")
            time.sleep(1)
            
            # Find password field
            password_selectors = [
                (By.ID, "password"),
                (By.NAME, "password"),
                (By.CSS_SELECTOR, "input[type='password']"),
                (By.CSS_SELECTOR, "input[placeholder*='password' i]"),
                (By.XPATH, "//input[@type='password']"),
            ]
            
            password_field = None
            for by, selector in password_selectors:
                try:
                    password_field = self.driver.find_element(by, selector)
                    if password_field:
                        logger.info(f"✅ Found password field with {by}: {selector}")
                        break
                except:
                    continue
            
            if not password_field:
                logger.error("❌ Could not find password field")
                return False
            
            # Enter password
            password_field.clear()
            password_field.send_keys(self.password)
            logger.info("✅ Password entered")
            time.sleep(1)
            
            # Find submit button
            submit_selectors = [
                (By.ID, "login"),
                (By.CSS_SELECTOR, "button[type='submit']"),
                (By.CSS_SELECTOR, "input[type='submit']"),
                (By.XPATH, "//button[contains(text(), 'Log in') or contains(text(), 'Login')]"),
                (By.XPATH, "//input[@type='submit' and @value*='Log' i]"),
                (By.CSS_SELECTOR, ".login-button, .submit-button"),
            ]
            
            submit_button = None
            for by, selector in submit_selectors:
                try:
                    submit_button = self.driver.find_element(by, selector)
                    if submit_button:
                        logger.info(f"✅ Found submit button with {by}: {selector}")
                        break
                except:
                    continue
            
            if not submit_button:
                # Try pressing Enter on password field
                logger.info("🔄 No submit button found, trying Enter key...")
                from selenium.webdriver.common.keys import Keys
                password_field.send_keys(Keys.RETURN)
            else:
                submit_button.click()
            
            logger.info("✅ Login submitted")
            time.sleep(5)
            
            # Check if login was successful
            current_url = self.driver.current_url.lower()
            page_text = self.driver.page_source.lower()
            
            if "account" in current_url or "server" in current_url or "panel" in current_url:
                logger.info("🎉 Login successful!")
                return True
            elif "captcha" in page_text:
                logger.error("🚨 CAPTCHA detected!")
                return False
            elif "incorrect" in page_text or "error" in page_text:
                logger.error("❌ Login error - wrong credentials?")
                return False
            else:
                # Check if we see dashboard elements
                dashboard_elements = [
                    "dashboard", "server", "start", "stop", "restart",
                    self.username.lower(), "minecraft", "aternos"
                ]
                
                page_lower = page_text.lower()
                if any(element in page_lower for element in dashboard_elements):
                    logger.info("✅ Likely logged in (dashboard elements found)")
                    return True
                else:
                    logger.warning("⚠️ Login status uncertain, but continuing...")
                    return True
                
        except Exception as e:
            logger.error(f"❌ Login error: {e}")
            return False
    
    def navigate_to_server(self):
        """Navigate to server control panel"""
        try:
            logger.info("🔄 Navigating to server...")
            
            # Try direct server URL first
            self.driver.get("https://aternos.org/server/")
            time.sleep(3)
            
            # Check if we're on server page
            page_text = self.driver.page_source.lower()
            if any(word in page_text for word in ['start', 'stop', 'restart', 'online', 'offline', 'server']):
                logger.info("✅ On server control panel")
                return True
            
            # Try servers list
            self.driver.get("https://aternos.org/servers/")
            time.sleep(2)
            
            # Look for our server
            server_name = self.server_url.split(':')[0]
            
            # Try different search patterns
            search_patterns = [
                server_name,
                server_name.replace('.aternos.me', ''),
                "gameplannet",
                "gameplan"
            ]
            
            for pattern in search_patterns:
                try:
                    elements = self.driver.find_elements(
                        By.XPATH, f"//*[contains(text(), '{pattern}') or contains(@title, '{pattern}') or contains(@href, '{pattern}')]"
                    )
                    if elements:
                        elements[0].click()
                        logger.info(f"✅ Found server: {pattern}")
                        time.sleep(3)
                        return True
                except:
                    continue
            
            # Fallback: look for any server element
            try:
                server_elements = self.driver.find_elements(
                    By.XPATH, "//div[contains(@class, 'server') or contains(@class, 'card')]//a | //div[contains(@class, 'server') or contains(@class, 'card')]//button"
                )
                if server_elements:
                    server_elements[0].click()
                    logger.info("✅ Clicked first server element")
                    time.sleep(3)
                    return True
            except:
                pass
            
            logger.warning("⚠️ Could not find specific server, trying to continue...")
            return True
            
        except Exception as e:
            logger.error(f"❌ Navigation error: {e}")
            return False
    
    def find_timer(self):
        """Find shutdown timer"""
        try:
            # Refresh page
            self.driver.refresh()
            time.sleep(2)
            
            # Get page content
            page_text = self.driver.page_source
            
            # Look for timer patterns
            timer_patterns = [
                r'0:5[0-9]',  # 0:50-0:59
                r'0:[0-5][0-9]',  # 0:00-0:59
                r'1:0[0-9]',  # 1:00-1:09
                r'\b\d:\d{2}\b',  # X:XX format
            ]
            
            for pattern in timer_patterns:
                matches = re.findall(pattern, page_text)
                if matches:
                    timer = matches[0]
                    logger.info(f"⏰ Found timer: {timer}")
                    return timer
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Timer search error: {e}")
            return None
    
    def find_plus_one_button(self):
        """Find +1 button"""
        try:
            # Look for +1 button
            boost_selectors = [
                "//button[text()='+1']",
                "//button[contains(text(), '+1')]",
                "//button[contains(text(), 'RAM') and contains(text(), 'boost')]",
                "//a[contains(text(), 'RAM') and contains(text(), 'boost')]",
                "//button[.//*[text()='+1']]",
                "//div[contains(text(), 'Boost your')]/following::button[1]",
            ]
            
            for selector in boost_selectors:
                try:
                    boost_btn = WebDriverWait(self.driver, 3).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    if boost_btn and boost_btn.is_displayed():
                        logger.info(f"🎯 Found +1 button: {selector}")
                        return boost_btn
                except:
                    continue
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Button search error: {e}")
            return None
    
    def click_plus_one(self, button):
        """Click +1 button"""
        try:
            logger.info("⚡ Clicking +1 button...")
            
            # Scroll and click
            self.driver.execute_script("arguments[0].scrollIntoView(true);", button)
            time.sleep(0.5)
            button.click()
            
            # Wait for action
            time.sleep(2)
            
            # Update stats
            self.total_clicks += 1
            self.consecutive_fails = 0
            
            logger.info(f"✅ +1 clicked! Total: {self.total_clicks}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Click error: {e}")
            self.consecutive_fails += 1
            return False
    
    def check_server_status(self):
        """Check server status"""
        try:
            page_text = self.driver.page_source
            
            if 'Online' in page_text or 'ONLINE' in page_text:
                logger.info("📊 Server status: Online")
                return 'online'
            elif 'Offline' in page_text or 'OFFLINE' in page_text:
                logger.info("📊 Server status: Offline")
                return 'offline'
            elif 'Starting' in page_text:
                logger.info("📊 Server status: Starting")
                return 'starting'
            
            return 'unknown'
            
        except Exception as e:
            logger.error(f"❌ Status check error: {e}")
            return 'error'
    
    def monitor(self):
        """Main monitoring loop"""
        logger.info("🚀 Starting monitoring...")
        
        check_count = 0
        
        while self.consecutive_fails < self.max_fails:
            check_count += 1
            
            # Log status
            if check_count % 5 == 0:
                elapsed = (datetime.now() - self.session_start).total_seconds() / 60
                logger.info(f"\n🔄 Check #{check_count} | ⏰ {elapsed:.1f}m | 🎯 {self.total_clicks} clicks")
            
            # Check server status
            status = self.check_server_status()
            
            if status == 'offline':
                logger.info("🔌 Server is offline")
                time.sleep(30)
                continue
            
            # Find timer
            timer = self.find_timer()
            
            if timer:
                if any(pattern in timer for pattern in ['0:59', '0:58', '0:57', '0:56']):
                    logger.info(f"🎯 CRITICAL: Timer at {timer}")
                    
                    # Find +1 button
                    button = self.find_plus_one_button()
                    
                    if button:
                        self.click_plus_one(button)
                        time.sleep(10)
                    else:
                        logger.info(f"⏳ No +1 button at {timer}")
                        time.sleep(10)
                else:
                    logger.info(f"⏰ Timer at {timer}, waiting...")
                    time.sleep(30)
            else:
                # Check for +1 button anyway
                button = self.find_plus_one_button()
                if button:
                    logger.info("🎯 Found +1 button without timer!")
                    self.click_plus_one(button)
                    time.sleep(10)
                else:
                    logger.info("🔍 No timer/button, waiting...")
                    time.sleep(45)
        
        logger.error(f"❌ Too many fails ({self.consecutive_fails})")
        return False
    
    def run(self):
        """Main run method"""
        try:
            # Setup driver
            if not self.setup_driver():
                return False
            
            # Login
            if not self.login():
                return False
            
            # Navigate to server
            if not self.navigate_to_server():
                logger.warning("⚠️ Navigation issues, but continuing...")
            
            # Start monitoring
            return self.monitor()
            
        except Exception as e:
            logger.error(f"❌ Fatal error: {e}")
            return False
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Cleanup"""
        try:
            if self.driver:
                self.driver.quit()
                logger.info("✅ Browser closed")
        except:
            pass


if __name__ == "__main__":
    keeper = Aternos24_7Keeper()
    keeper.run()
