import os
import time
import logging
import random
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException

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
    Keeps Aternos server running 24/7 by clicking +1 button at 0:59
    Optimized for Render with Chrome compatibility fixes
    """
    
    def __init__(self, username=None, password=None, server_url=None):
        """
        Initialize the 24/7 server keeper
        
        Args:
            username: Aternos username (default from env: _CRAFTEEE_)
            password: Aternos password (default from env: Albin4242)
            server_url: Server address (default from env: gameplannet.aternos.me:43658)
        """
        # Get credentials from environment or parameters
        self.username = username or os.getenv('ATERNOS_USERNAME', '_CRAFTEEE_')
        self.password = password or os.getenv('ATERNOS_PASSWORD', 'Albin4242')
        self.server_url = server_url or os.getenv('ATERNOS_SERVER', 'gameplannet.aternos.me:43658')
        
        # Configuration
        self.driver = None
        self.session_start = datetime.now()
        self.total_clicks = 0
        self.consecutive_fails = 0
        self.max_fails = int(os.getenv('MAX_FAILURES', '10'))
        self.stealth_mode = os.getenv('STEALTH_MODE', 'false').lower() == 'true'
        self.is_running = False
        self.last_refresh = 0
        self.last_click = None
        
        logger.info("=" * 60)
        logger.info("🎮 ATORNOS 24/7 SERVER KEEPER INITIALIZED")
        logger.info(f"👤 Username: {self.username}")
        logger.info(f"🌐 Server: {self.server_url}")
        logger.info(f"🛡️ Stealth mode: {self.stealth_mode}")
        logger.info(f"🎯 Strategy: Click +1 button at 0:59 to reset shutdown timer")
        logger.info("🔥 Goal: Keep server running 24/7 FOREVER!")
        logger.info("=" * 60)
    
    def setup_driver(self):
        """Setup Chrome driver optimized for Render with multiple fallbacks"""
        try:
            logger.info("🚀 Setting up Chrome driver for Render...")
            
            options = ChromeOptions()
            
            # Essential arguments for Render
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--window-size=1920,1080')
            options.add_argument('--disable-extensions')
            
            # For Render/Chromium compatibility
            options.binary_location = '/usr/bin/chromium-browser'
            
            # Anti-detection if stealth mode
            if self.stealth_mode:
                options.add_argument('--disable-blink-features=AutomationControlled')
                options.add_experimental_option("excludeSwitches", ["enable-automation"])
                options.add_experimental_option('useAutomationExtension', False)
                
                # User agent
                user_agents = [
                    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                ]
                options.add_argument(f'user-agent={random.choice(user_agents)}')
            else:
                # Simple user agent for non-stealth
                options.add_argument('user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            
            logger.info("📦 Attempting to setup ChromeDriver...")
            
            try:
                # Method 1: Try webdriver-manager first
                from selenium.webdriver.chrome.service import Service
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=options)
                logger.info("✅ Driver setup with webdriver-manager")
                
            except Exception as e1:
                logger.warning(f"⚠️ webdriver-manager failed: {e1}")
                
                try:
                    # Method 2: Try direct Chrome with local driver
                    self.driver = webdriver.Chrome(options=options)
                    logger.info("✅ Driver setup with direct Chrome")
                    
                except Exception as e2:
                    logger.warning(f"⚠️ Direct Chrome failed: {e2}")
                    
                    try:
                        # Method 3: Try Chromium explicitly
                        options.binary_location = '/usr/bin/chromium-browser'
                        self.driver = webdriver.Chrome(options=options)
                        logger.info("✅ Driver setup with Chromium")
                        
                    except Exception as e3:
                        logger.error(f"❌ All driver setup methods failed: {e3}")
                        return False
            
            # Basic anti-detection
            try:
                self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                logger.info("✅ Anti-detection script executed")
            except:
                logger.warning("⚠️ Could not execute anti-detection script")
            
            logger.info("✅ Chrome driver initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to setup driver: {e}")
            
            # Final fallback: Try with minimal options
            try:
                logger.info("🔄 Trying minimal driver setup...")
                options = ChromeOptions()
                options.add_argument('--headless')
                options.add_argument('--no-sandbox')
                options.add_argument('--disable-dev-shm-usage')
                
                self.driver = webdriver.Chrome(options=options)
                logger.info("✅ Minimal driver setup successful")
                return True
            except Exception as e2:
                logger.error(f"❌ Minimal setup also failed: {e2}")
                return False
    
    def human_delay(self, min_seconds=1, max_seconds=3):
        """Random delay to mimic human behavior"""
        if not self.stealth_mode:
            time.sleep(min_seconds)
            return min_seconds
        
        delay = random.uniform(min_seconds, max_seconds)
        time.sleep(delay)
        return delay
    
    def random_mouse_movement(self):
        """Simulate random mouse movements (stealth only)"""
        try:
            if not self.stealth_mode:
                return False
                
            actions = ActionChains(self.driver)
            actions.move_by_offset(random.randint(-20, 20), random.randint(-20, 20))
            actions.perform()
            time.sleep(random.uniform(0.1, 0.3))
            return True
        except:
            return False
    
    def random_scroll(self):
        """Random scroll (stealth only)"""
        try:
            if not self.stealth_mode or random.random() > 0.3:
                return False
                
            scroll_amount = random.randint(100, 300)
            self.driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
            time.sleep(random.uniform(0.2, 0.5))
            return True
        except:
            return False
    
    def login(self):
        """Login to Aternos"""
        try:
            logger.info(f"🔐 Logging in as {self.username}...")
            
            # Go to Aternos
            self.driver.get("https://aternos.org/")
            self.human_delay(2, 3)
            
            # Find login button
            login_selectors = [
                "//button[contains(., 'Log in')]",
                "//a[contains(@href, 'login')]",
                "//button[contains(@class, 'login')]"
            ]
            
            login_clicked = False
            for selector in login_selectors:
                try:
                    login_btn = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    login_btn.click()
                    login_clicked = True
                    logger.info("✅ Login button clicked")
                    self.human_delay(1, 2)
                    break
                except:
                    continue
            
            # Fallback to direct login page
            if not login_clicked:
                logger.info("🔄 Trying direct login page...")
                self.driver.get("https://aternos.org/account/")
                self.human_delay(2, 3)
            
            # Enter username
            username_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "user"))
            )
            username_field.send_keys(self.username)
            logger.info("✅ Username entered")
            self.human_delay(0.5, 1)
            
            # Enter password
            pass_field = self.driver.find_element(By.ID, "password")
            pass_field.send_keys(self.password)
            logger.info("✅ Password entered")
            self.human_delay(0.5, 1)
            
            # Submit login
            submit_selectors = [
                (By.ID, "login"),
                (By.XPATH, "//button[@type='submit']"),
                (By.XPATH, "//button[contains(., 'Log in')]")
            ]
            
            for by, selector in submit_selectors:
                try:
                    submit_btn = self.driver.find_element(by, selector)
                    if submit_btn:
                        submit_btn.click()
                        logger.info("✅ Login submitted")
                        break
                except:
                    continue
            
            # Wait for login
            self.human_delay(3, 4)
            
            # Check login success
            current_url = self.driver.current_url.lower()
            if "account" in current_url or "server" in current_url or "panel" in current_url:
                logger.info("🎉 Login successful!")
                return True
            else:
                # Check for errors
                page_text = self.driver.page_source.lower()
                if "captcha" in page_text:
                    logger.error("🚨 CAPTCHA detected!")
                    return False
                elif "error" in page_text or "incorrect" in page_text:
                    logger.error("❌ Login error detected")
                    return False
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
            
            # Try direct server URL
            self.driver.get("https://aternos.org/server/")
            self.human_delay(3, 4)
            
            # Check if we're on server page
            page_text = self.driver.page_source.lower()
            server_keywords = ["start", "stop", "restart", "online", "offline", "server", "players", "ram"]
            
            if any(keyword in page_text for keyword in server_keywords):
                logger.info("✅ On server control panel")
                return True
            
            # Try servers list
            logger.info("🔍 Trying servers list...")
            self.driver.get("https://aternos.org/servers/")
            self.human_delay(2, 3)
            
            # Look for server by name
            server_name = self.server_url.split(':')[0]
            variations = [server_name, "gameplannet"]
            
            for variation in variations:
                try:
                    server_elements = self.driver.find_elements(
                        By.XPATH, f"//*[contains(text(), '{variation}')]"
                    )
                    
                    if server_elements:
                        logger.info(f"✅ Found server: {variation}")
                        server_elements[0].click()
                        self.human_delay(2, 3)
                        return True
                except:
                    continue
            
            # Fallback: click first server card
            try:
                server_cards = self.driver.find_elements(
                    By.XPATH, "//div[contains(@class, 'card') or contains(@class, 'server')]//a | //div[contains(@class, 'card') or contains(@class, 'server')]//button"
                )
                if server_cards:
                    logger.info(f"🔗 Clicking first server element")
                    server_cards[0].click()
                    self.human_delay(2, 3)
                    return True
            except:
                pass
            
            logger.warning("⚠️ Could not find specific server, continuing anyway...")
            return True
            
        except Exception as e:
            logger.error(f"❌ Navigation error: {e}")
            return False
    
    def find_shutdown_timer(self):
        """Find the shutdown timer (0:59, 1:00, etc.)"""
        try:
            # Get page content
            page_text = self.driver.page_source
            
            # Look for timer patterns
            import re
            
            # Common timer patterns
            timer_patterns = [
                r'0:5[0-9]',  # 0:50-0:59
                r'0:[0-5][0-9]',  # 0:00-0:59
                r'1:0[0-9]',  # 1:00-1:09
                r'\d:\d{2}',  # Any X:XX
            ]
            
            for pattern in timer_patterns:
                matches = re.findall(pattern, page_text)
                if matches:
                    # Return first match
                    timer = matches[0]
                    if len(timer) <= 5:  # Validate format
                        logger.info(f"⏰ Found timer: {timer}")
                        return timer
            
            # Also look for text containing countdown
            countdown_words = ['minute', 'second', 'countdown', 'shutdown', 'timer']
            page_lower = page_text.lower()
            for word in countdown_words:
                if word in page_lower:
                    logger.info(f"⏰ Countdown indicator: {word}")
                    return f"countdown_{word}"
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Timer search error: {e}")
            return None
    
    def find_plus_one_button(self):
        """Find the +1 button"""
        try:
            # Refresh page occasionally
            current_time = time.time()
            if current_time - self.last_refresh > 30:
                logger.info("🔄 Refreshing page...")
                self.driver.refresh()
                self.last_refresh = current_time
                self.human_delay(2, 3)
            
            # Look for +1 button
            boost_selectors = [
                "//button[text()='+1']",  # Exact match
                "//button[contains(text(), '+1')]",
                "//button[contains(text(), 'RAM boost')]",
                "//a[contains(text(), 'RAM boost')]",
                "//button[.//*[text()='+1']]",
                "//button[@aria-label*='boost' or @aria-label*='+1']",
            ]
            
            for selector in boost_selectors:
                try:
                    boost_btn = WebDriverWait(self.driver, 3).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    
                    if boost_btn and boost_btn.is_displayed() and boost_btn.is_enabled():
                        logger.info(f"🎯 Found +1 button")
                        return boost_btn
                except:
                    continue
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Button search error: {e}")
            return None
    
    def click_plus_one_button(self, button):
        """Click the +1 button"""
        try:
            logger.info("⚡ Clicking +1 button...")
            
            # Scroll to button
            self.driver.execute_script("arguments[0].scrollIntoView(true);", button)
            self.human_delay(0.2, 0.5)
            
            # Click using JavaScript (most reliable)
            self.driver.execute_script("arguments[0].click();", button)
            
            # Wait for action
            self.human_delay(1, 2)
            
            # Update stats
            self.total_clicks += 1
            self.last_click = datetime.now()
            self.consecutive_fails = 0
            
            logger.info(f"✅ +1 button clicked! Total clicks: {self.total_clicks}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Click error: {e}")
            self.consecutive_fails += 1
            return False
    
    def check_server_status(self):
        """Check if server is online/offline"""
        try:
            # Look for status indicators
            page_text = self.driver.page_source
            
            if 'Online' in page_text or 'ONLINE' in page_text:
                logger.info("📊 Server status: Online")
                return 'online'
            elif 'Offline' in page_text or 'OFFLINE' in page_text or 'Stopped' in page_text:
                logger.info("📊 Server status: Offline")
                return 'offline'
            elif 'Starting' in page_text:
                logger.info("📊 Server status: Starting")
                return 'starting'
            
            # Check for buttons
            try:
                start_buttons = self.driver.find_elements(
                    By.XPATH, "//button[contains(text(), 'Start') and not(contains(text(), 'Restart'))]"
                )
                if start_buttons:
                    logger.info("📊 Server appears offline (Start button found)")
                    return 'offline'
                
                stop_buttons = self.driver.find_elements(
                    By.XPATH, "//button[contains(text(), 'Stop')]"
                )
                if stop_buttons:
                    logger.info("📊 Server appears online (Stop button found)")
                    return 'online'
            except:
                pass
            
            return 'unknown'
            
        except Exception as e:
            logger.error(f"❌ Status check error: {e}")
            return 'error'
    
    def start_server_if_needed(self):
        """Start the server if it's offline"""
        try:
            status = self.check_server_status()
            
            if status == 'offline':
                logger.info("🚀 Server is offline, attempting to start...")
                
                start_selectors = [
                    "//button[contains(text(), 'Start') and not(contains(text(), 'Restart'))]",
                    "//button[@id='start']",
                    "//button[contains(@class, 'start')]",
                ]
                
                for selector in start_selectors:
                    try:
                        start_btn = WebDriverWait(self.driver, 5).until(
                            EC.element_to_be_clickable((By.XPATH, selector))
                        )
                        if start_btn:
                            start_btn.click()
                            logger.info("✅ Start button clicked, waiting 60 seconds...")
                            
                            # Wait for server to start
                            for i in range(6):
                                time.sleep(10)
                                new_status = self.check_server_status()
                                if new_status == 'online' or new_status == 'starting':
                                    logger.info(f"✅ Server is {new_status}")
                                    return True
                            
                            logger.warning("⚠️ Server may still be starting...")
                            return False
                    except:
                        continue
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Start server error: {e}")
            return False
    
    def monitor_and_keep_alive(self):
        """Main monitoring loop"""
        logger.info("🚀 Starting 24/7 server keeper monitoring...")
        
        try:
            # Setup driver
            if not self.setup_driver():
                logger.error("❌ Driver setup failed")
                return False
            
            # Login
            if not self.login():
                logger.error("❌ Login failed")
                return False
            
            # Navigate to server
            if not self.navigate_to_server():
                logger.warning("⚠️ Navigation had issues, but continuing...")
            
            self.is_running = True
            check_count = 0
            
            while self.is_running and self.consecutive_fails < self.max_fails:
                check_count += 1
                elapsed_minutes = (datetime.now() - self.session_start).total_seconds() / 60
                
                # Log status periodically
                if check_count % 10 == 0:
                    logger.info(f"\n{'='*50}")
                    logger.info(f"🔄 Check #{check_count}")
                    logger.info(f"⏰ Runtime: {elapsed_minutes:.1f} minutes")
                    logger.info(f"🎯 Total +1 clicks: {self.total_clicks}")
                    logger.info(f"❌ Consecutive fails: {self.consecutive_fails}")
                    
                    if self.last_click:
                        seconds_since_click = (datetime.now() - self.last_click).seconds
                        logger.info(f"⏱️ Since last click: {seconds_since_click} seconds")
                    
                    logger.info(f"{'='*50}")
                
                # Check server status
                status = self.check_server_status()
                
                if status == 'offline':
                    logger.info("🔌 Server offline, trying to start...")
                    if self.start_server_if_needed():
                        time.sleep(30)
                        continue
                    else:
                        logger.error("❌ Failed to start server")
                        self.consecutive_fails += 1
                        time.sleep(30)
                        continue
                
                # Find shutdown timer
                timer = self.find_shutdown_timer()
                
                if timer:
                    # Check if timer is critical
                    if any(pattern in timer for pattern in ['0:59', '0:58', '0:57', '0:56']):
                        logger.info(f"🎯 CRITICAL TIMER: {timer}! Looking for +1 button...")
                        
                        # Look for +1 button
                        plus_one_btn = self.find_plus_one_button()
                        
                        if plus_one_btn:
                            # CLICK IT!
                            if self.click_plus_one_button(plus_one_btn):
                                logger.info(f"✅ +1 clicked! Timer should reset.")
                                
                                # Wait for timer to reset
                                time.sleep(5)
                            else:
                                logger.error("❌ Failed to click +1 button")
                                self.consecutive_fails += 1
                        else:
                            logger.info(f"⏳ Timer at {timer} but no +1 button yet")
                            time.sleep(10)
                    elif '1:00' in timer or '0:45' in timer:
                        logger.info(f"⏰ Timer at {timer}, waiting...")
                        time.sleep(20)
                    else:
                        logger.info(f"⏰ Timer at {timer}, waiting longer...")
                        time.sleep(30)
                else:
                    # No timer found, check for +1 button anyway
                    logger.info("🔍 No timer found, checking for +1 button...")
                    plus_one_btn = self.find_plus_one_button()
                    
                    if plus_one_btn:
                        logger.info("🎯 Found +1 button without timer!")
                        self.click_plus_one_button(plus_one_btn)
                    else:
                        logger.info("🔍 Nothing found, waiting 45 seconds...")
                        time.sleep(45)
                
                # Recovery check
                if self.consecutive_fails >= 3:
                    logger.warning(f"🔄 {self.consecutive_fails} consecutive fails, attempting recovery...")
                    self.driver.refresh()
                    self.last_refresh = time.time()
                    time.sleep(5)
            
            # Loop ended
            if self.consecutive_fails >= self.max_fails:
                logger.error(f"❌ Too many consecutive fails ({self.consecutive_fails}), stopping...")
            else:
                logger.info("🛑 Monitoring stopped")
            
            return True
            
        except KeyboardInterrupt:
            logger.info("\n👋 Stopped by user")
            return True
        except Exception as e:
            logger.error(f"❌ Fatal error in monitoring: {e}")
            return False
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Cleanup resources"""
        try:
            if self.driver:
                self.driver.quit()
                logger.info("✅ Browser closed")
        except:
            pass
    
    def run(self):
        """Main run method"""
        return self.monitor_and_keep_alive()


# Quick test
if __name__ == "__main__":
    keeper = Aternos24_7Keeper()
    keeper.run()
