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
from selenium.webdriver.chrome.service import Service
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
    Optimized Aternos 24/7 Server Keeper
    Fixed for Render with proper Chrome setup
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
        logger.info("🎮 ATORNOS 24/7 SERVER KEEPER")
        logger.info(f"👤 Username: {self.username}")
        logger.info(f"🌐 Server: {self.server_url}")
        logger.info("🎯 Strategy: Click +1 button at 0:59")
        logger.info("=" * 60)
    
    def setup_driver_simple(self):
        """Simple driver setup that works on Render"""
        try:
            logger.info("🚀 Setting up Chrome driver...")
            
            options = ChromeOptions()
            
            # Basic arguments for Render
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--window-size=1920,1080')
            options.add_argument('--disable-extensions')
            
            # For Chromium on Render
            options.binary_location = '/usr/bin/chromium-browser'
            
            # Simple user agent
            options.add_argument('user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            
            # Disable automation detection
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            # Create driver
            logger.info("🛠️ Creating Chrome driver...")
            self.driver = webdriver.Chrome(options=options)
            
            # Anti-detection
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            logger.info("✅ Chrome driver initialized")
            return True
            
        except Exception as e:
            logger.error(f"❌ Driver setup failed: {e}")
            
            # Try one more time with minimal options
            try:
                logger.info("🔄 Trying minimal setup...")
                options = ChromeOptions()
                options.add_argument('--headless')
                options.add_argument('--no-sandbox')
                options.add_argument('--disable-dev-shm-usage')
                
                self.driver = webdriver.Chrome(options=options)
                logger.info("✅ Minimal driver setup successful")
                return True
            except Exception as e2:
                logger.error(f"❌ Minimal setup failed: {e2}")
                return False
    
    def login_simple(self):
        """Simple login method"""
        try:
            logger.info(f"🔐 Logging in as {self.username}...")
            
            # Go to Aternos
            self.driver.get("https://aternos.org/")
            time.sleep(3)
            
            # Try to find login button
            try:
                login_btn = self.driver.find_element(By.XPATH, "//button[contains(., 'Log in')]")
                login_btn.click()
                time.sleep(2)
            except:
                # Go to login page directly
                self.driver.get("https://aternos.org/account/")
                time.sleep(3)
            
            # Enter username
            try:
                user_field = self.driver.find_element(By.ID, "user")
                user_field.send_keys(self.username)
                logger.info("✅ Username entered")
                time.sleep(1)
            except:
                logger.error("❌ Could not find username field")
                return False
            
            # Enter password
            try:
                pass_field = self.driver.find_element(By.ID, "password")
                pass_field.send_keys(self.password)
                logger.info("✅ Password entered")
                time.sleep(1)
            except:
                logger.error("❌ Could not find password field")
                return False
            
            # Submit login
            try:
                submit_btn = self.driver.find_element(By.ID, "login")
                submit_btn.click()
                logger.info("✅ Login submitted")
                time.sleep(5)
            except:
                # Try alternative submit button
                try:
                    submit_btn = self.driver.find_element(By.XPATH, "//button[@type='submit']")
                    submit_btn.click()
                    logger.info("✅ Login submitted (alternative)")
                    time.sleep(5)
                except:
                    logger.warning("⚠️ Could not find submit button, but continuing...")
            
            # Check if login was successful
            current_url = self.driver.current_url.lower()
            if "account" in current_url or "server" in current_url:
                logger.info("🎉 Login successful!")
                return True
            else:
                # Check page content
                page_text = self.driver.page_source.lower()
                if "captcha" in page_text:
                    logger.error("🚨 CAPTCHA detected!")
                    return False
                elif "error" in page_text:
                    logger.error("❌ Login error detected")
                    return False
                else:
                    logger.warning("⚠️ Login status uncertain, but continuing...")
                    return True
                
        except Exception as e:
            logger.error(f"❌ Login error: {e}")
            return False
    
    def go_to_server_simple(self):
        """Simple navigation to server"""
        try:
            logger.info("🔄 Going to server...")
            
            # Try direct server URL
            self.driver.get("https://aternos.org/server/")
            time.sleep(3)
            
            # Check if we're on server page
            page_text = self.driver.page_source.lower()
            if any(word in page_text for word in ['start', 'stop', 'restart', 'online', 'offline']):
                logger.info("✅ On server control panel")
                return True
            
            # Try servers list
            self.driver.get("https://aternos.org/servers/")
            time.sleep(2)
            
            # Look for server by name
            server_name = self.server_url.split(':')[0]
            
            # Try to find server element
            try:
                server_elements = self.driver.find_elements(
                    By.XPATH, f"//*[contains(text(), '{server_name}')]"
                )
                if server_elements:
                    server_elements[0].click()
                    time.sleep(3)
                    logger.info(f"✅ Found and clicked server: {server_name}")
                    return True
            except:
                pass
            
            # Click first server card
            try:
                server_cards = self.driver.find_elements(
                    By.XPATH, "//div[contains(@class, 'card') or contains(@class, 'server')]//a | //div[contains(@class, 'card') or contains(@class, 'server')]//button"
                )
                if server_cards:
                    server_cards[0].click()
                    time.sleep(3)
                    logger.info("✅ Clicked first server card")
                    return True
            except:
                pass
            
            logger.warning("⚠️ Could not navigate to specific server, but continuing...")
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
            ]
            
            for pattern in timer_patterns:
                matches = re.findall(pattern, page_text)
                if matches:
                    timer = matches[0]
                    logger.info(f"⏰ Found timer: {timer}")
                    return timer
            
            # Look for countdown text
            countdown_words = ['minute', 'second', 'countdown', 'shutdown', 'timer']
            page_lower = page_text.lower()
            for word in countdown_words:
                if word in page_lower:
                    logger.info(f"⏰ Found countdown indicator: {word}")
                    return f"countdown_{word}"
            
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
                "//button[contains(text(), 'RAM boost')]",
                "//a[contains(text(), 'RAM boost')]",
                "//button[.//*[text()='+1']]",
            ]
            
            for selector in boost_selectors:
                try:
                    boost_btn = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    if boost_btn and boost_btn.is_displayed():
                        logger.info("🎯 Found +1 button")
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
            self.driver.execute_script("arguments[0].click();", button)
            
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
                return 'online'
            elif 'Offline' in page_text or 'OFFLINE' in page_text:
                return 'offline'
            elif 'Starting' in page_text:
                return 'starting'
            
            # Check buttons
            try:
                start_buttons = self.driver.find_elements(
                    By.XPATH, "//button[contains(text(), 'Start')]"
                )
                if start_buttons:
                    return 'offline'
                
                stop_buttons = self.driver.find_elements(
                    By.XPATH, "//button[contains(text(), 'Stop')]"
                )
                if stop_buttons:
                    return 'online'
            except:
                pass
            
            return 'unknown'
            
        except Exception as e:
            logger.error(f"❌ Status check error: {e}")
            return 'error'
    
    def start_server(self):
        """Start server if offline"""
        try:
            logger.info("🚀 Starting server...")
            
            start_selectors = [
                "//button[contains(text(), 'Start')]",
                "//button[@id='start']",
            ]
            
            for selector in start_selectors:
                try:
                    start_btn = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    start_btn.click()
                    logger.info("✅ Start button clicked")
                    
                    # Wait for server to start
                    for i in range(10):
                        time.sleep(10)
                        status = self.check_server_status()
                        if status in ['online', 'starting']:
                            logger.info(f"✅ Server is {status}")
                            return True
                    
                    logger.warning("⚠️ Server may still be starting...")
                    return False
                except:
                    continue
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Start error: {e}")
            return False
    
    def monitor_loop(self):
        """Main monitoring loop"""
        logger.info("🚀 Starting monitoring loop...")
        
        check_count = 0
        
        while self.consecutive_fails < self.max_fails:
            check_count += 1
            elapsed_minutes = (datetime.now() - self.session_start).total_seconds() / 60
            
            # Log status
            if check_count % 5 == 0:
                logger.info(f"\n{'='*40}")
                logger.info(f"🔄 Check #{check_count}")
                logger.info(f"⏰ Runtime: {elapsed_minutes:.1f}m")
                logger.info(f"🎯 Clicks: {self.total_clicks}")
                logger.info(f"❌ Fails: {self.consecutive_fails}")
                logger.info(f"{'='*40}")
            
            # Check server status
            status = self.check_server_status()
            
            if status == 'offline':
                logger.info("🔌 Server offline, starting...")
                if self.start_server():
                    time.sleep(30)
                    continue
                else:
                    logger.error("❌ Failed to start server")
                    self.consecutive_fails += 1
                    time.sleep(30)
                    continue
            
            # Find timer
            timer = self.find_timer()
            
            if timer:
                # Check if timer is critical
                if any(pattern in timer for pattern in ['0:59', '0:58', '0:57']):
                    logger.info(f"🎯 Timer at {timer}! Looking for +1...")
                    
                    # Find +1 button
                    plus_one_btn = self.find_plus_one_button()
                    
                    if plus_one_btn:
                        if self.click_plus_one(plus_one_btn):
                            logger.info("✅ +1 clicked, timer should reset")
                            time.sleep(10)
                        else:
                            logger.error("❌ Failed to click +1")
                            time.sleep(10)
                    else:
                        logger.info(f"⏳ No +1 button at {timer}")
                        time.sleep(15)
                else:
                    logger.info(f"⏰ Timer at {timer}, waiting...")
                    time.sleep(30)
            else:
                # Check for +1 button anyway
                plus_one_btn = self.find_plus_one_button()
                if plus_one_btn:
                    logger.info("🎯 Found +1 button without timer!")
                    self.click_plus_one(plus_one_btn)
                    time.sleep(10)
                else:
                    logger.info("🔍 No timer or button, waiting...")
                    time.sleep(45)
            
            # Check for too many fails
            if self.consecutive_fails >= 3:
                logger.warning(f"🔄 {self.consecutive_fails} fails, refreshing...")
                self.driver.refresh()
                time.sleep(5)
        
        logger.error(f"❌ Too many fails ({self.consecutive_fails}), stopping")
        return False
    
    def run(self):
        """Main run method"""
        try:
            # Setup driver
            if not self.setup_driver_simple():
                logger.error("❌ Driver setup failed")
                return False
            
            # Login
            if not self.login_simple():
                logger.error("❌ Login failed")
                return False
            
            # Go to server
            if not self.go_to_server_simple():
                logger.warning("⚠️ Navigation issues, but continuing...")
            
            # Start monitoring
            return self.monitor_loop()
            
        except KeyboardInterrupt:
            logger.info("👋 Stopped by user")
            return True
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
