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
    Uses stealth techniques to avoid bot detection
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
        self.max_fails = int(os.getenv('MAX_FAILURES', '20'))
        self.stealth_mode = os.getenv('STEALTH_MODE', 'true').lower() == 'true'
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
        """Setup Chrome driver with stealth features"""
        try:
            logger.info("🚀 Setting up Chrome driver...")
            
            options = ChromeOptions()
            
            # Essential arguments for Render
            options.add_argument('--headless=new')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--window-size=1920,1080')
            
            if self.stealth_mode:
                # Stealth mode: Anti-detection features
                options.add_argument('--disable-blink-features=AutomationControlled')
                options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
                options.add_experimental_option('useAutomationExtension', False)
                
                # Random user agent
                user_agents = [
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.6045.159 Safari/537.36',
                    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36 Edg/118.0.2088.76',
                ]
                options.add_argument(f'user-agent={random.choice(user_agents)}')
            
            # Install ChromeDriver
            logger.info("📦 Installing ChromeDriver...")
            service = Service(ChromeDriverManager().install())
            
            # Create driver
            self.driver = webdriver.Chrome(service=service, options=options)
            
            # Execute stealth scripts if enabled
            if self.stealth_mode:
                stealth_js = """
                // Remove webdriver property
                Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                
                // Override plugins
                Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
                
                // Override languages
                Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
                
                // Mock Chrome runtime
                window.chrome = {runtime: {}};
                
                // Mock permissions
                const originalQuery = window.navigator.permissions.query;
                window.navigator.permissions.query = (parameters) => (
                    parameters.name === 'notifications' ?
                        Promise.resolve({state: Notification.permission}) :
                        originalQuery(parameters)
                );
                """
                self.driver.execute_script(stealth_js)
            
            logger.info("✅ Chrome driver setup complete")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to setup driver: {e}")
            return False
    
    def human_delay(self, min_seconds=1, max_seconds=3):
        """Random delay to mimic human behavior"""
        delay = random.uniform(min_seconds, max_seconds)
        time.sleep(delay)
        return delay
    
    def random_mouse_movement(self):
        """Simulate random mouse movements"""
        try:
            if not self.stealth_mode:
                return False
                
            actions = ActionChains(self.driver)
            
            # 1-3 random movements
            for _ in range(random.randint(1, 3)):
                x_offset = random.randint(-50, 50)
                y_offset = random.randint(-50, 50)
                actions.move_by_offset(x_offset, y_offset)
                actions.pause(random.uniform(0.1, 0.3))
            
            actions.perform()
            return True
        except:
            return False
    
    def random_scroll(self):
        """Random scroll to mimic human"""
        try:
            if not self.stealth_mode or random.random() > 0.5:
                return False
                
            scroll_amount = random.randint(100, 300)
            self.driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
            time.sleep(random.uniform(0.3, 1.0))
            
            # Sometimes scroll back
            if random.random() > 0.7:
                self.driver.execute_script(f"window.scrollBy(0, -{scroll_amount//2});")
                time.sleep(random.uniform(0.2, 0.8))
            
            return True
        except:
            return False
    
    def login(self):
        """Login to Aternos with human-like behavior"""
        try:
            logger.info(f"🔐 Logging in as {self.username}...")
            
            # Go to Aternos
            self.driver.get("https://aternos.org/")
            self.human_delay(2, 4)
            
            # Random activity if stealth mode
            if self.stealth_mode:
                self.random_mouse_movement()
            
            # Find login button
            login_selectors = [
                "//button[contains(., 'Log in')]",
                "//a[contains(@href, 'login')]",
                "//span[contains(., 'Log in')]/.."
            ]
            
            login_clicked = False
            for selector in login_selectors:
                try:
                    wait_time = random.randint(5, 8) if self.stealth_mode else 10
                    login_btn = WebDriverWait(self.driver, wait_time).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    
                    if self.stealth_mode:
                        # Human-like click with hover
                        actions = ActionChains(self.driver)
                        actions.move_to_element(login_btn)
                        actions.pause(random.uniform(0.2, 0.8))
                        actions.click()
                        actions.perform()
                    else:
                        # Direct click
                        login_btn.click()
                    
                    login_clicked = True
                    logger.info("✅ Login button clicked")
                    self.human_delay(1, 2)
                    break
                except:
                    continue
            
            # Fallback to direct login page
            if not login_clicked:
                self.driver.get("https://aternos.org/account/")
                self.human_delay(2, 3)
            
            # Enter username
            username_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "user"))
            )
            
            # Type like human if stealth mode
            if self.stealth_mode:
                for char in self.username:
                    username_field.send_keys(char)
                    time.sleep(random.uniform(0.05, 0.15))
            else:
                username_field.send_keys(self.username)
            
            self.human_delay(0.5, 1)
            
            # Enter password
            pass_field = self.driver.find_element(By.ID, "password")
            
            if self.stealth_mode:
                for char in self.password:
                    pass_field.send_keys(char)
                    time.sleep(random.uniform(0.05, 0.15))
            else:
                pass_field.send_keys(self.password)
            
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
                        if self.stealth_mode:
                            # Random activity before submit
                            if random.random() > 0.5:
                                self.random_scroll()
                            
                            # Click with offset
                            actions = ActionChains(self.driver)
                            actions.move_to_element_with_offset(
                                submit_btn, 
                                random.randint(-5, 5), 
                                random.randint(-5, 5)
                            )
                            actions.pause(random.uniform(0.1, 0.5))
                            actions.click()
                            actions.perform()
                        else:
                            submit_btn.click()
                        
                        logger.info("✅ Login submitted")
                        break
                except:
                    continue
            
            # Wait for login
            self.human_delay(3, 5)
            
            # Check login success
            current_url = self.driver.current_url.lower()
            if "account" in current_url or "server" in current_url or "panel" in current_url:
                logger.info("🎉 Login successful!")
                
                # Random activity after login
                if self.stealth_mode:
                    self.random_scroll()
                    self.random_mouse_movement()
                
                return True
            else:
                # Check for CAPTCHA or errors
                page_text = self.driver.page_source.lower()
                if "captcha" in page_text:
                    logger.error("🚨 CAPTCHA detected! Manual intervention needed.")
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
            self.human_delay(3, 5)
            
            # Check if we're on server page
            page_text = self.driver.page_source.lower()
            server_keywords = ["start", "stop", "restart", "online", "offline", "server", "players"]
            
            if any(keyword in page_text for keyword in server_keywords):
                logger.info("✅ On server control panel")
                return True
            
            # Try servers list
            logger.info("🔍 Trying servers list...")
            self.driver.get("https://aternos.org/servers/")
            self.human_delay(2, 3)
            
            # Look for server by name (remove port)
            server_name = self.server_url.split(':')[0]
            variations = [server_name, "gameplannet", "gameplan"]
            
            for variation in variations:
                try:
                    server_elements = self.driver.find_elements(
                        By.XPATH, f"//*[contains(text(), '{variation}')]"
                    )
                    
                    if server_elements:
                        logger.info(f"✅ Found server: {variation}")
                        if self.stealth_mode:
                            actions = ActionChains(self.driver)
                            actions.move_to_element(server_elements[0])
                            actions.pause(0.2)
                            actions.click()
                            actions.perform()
                        else:
                            server_elements[0].click()
                        
                        self.human_delay(2, 3)
                        return True
                except:
                    continue
            
            # Fallback: click first server card
            try:
                server_cards = self.driver.find_elements(
                    By.XPATH, "//div[contains(@class, 'card') or contains(@class, 'server')]//a"
                )
                if server_cards:
                    logger.info(f"🔗 Clicking first server card")
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
            
            # Look for timer patterns (0:59, 1:00, etc.)
            import re
            
            # Timer patterns (MM:SS or M:SS)
            timer_patterns = [
                r'0:5[0-9]',  # 0:50-0:59
                r'0:[0-5][0-9]',  # 0:00-0:59
                r'1:0[0-9]',  # 1:00-1:09
                r'\d:\d{2}',  # Any X:XX format
            ]
            
            for pattern in timer_patterns:
                matches = re.findall(pattern, page_text)
                if matches:
                    # Get unique matches
                    unique_timers = list(set(matches))
                    for timer in unique_timers:
                        # Validate it's a timer (not random numbers)
                        if len(timer) <= 5 and ':' in timer:
                            logger.info(f"⏰ Found timer: {timer}")
                            return timer
            
            # Also check for text indicating countdown
            countdown_words = ['minute', 'second', 'countdown', 'shutdown', 'auto-stop', 'timer']
            for word in countdown_words:
                if word in page_text.lower():
                    logger.info(f"⏰ Countdown indicator: {word}")
                    return f"countdown_{word}"
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Timer search error: {e}")
            return None
    
    def find_plus_one_button(self):
        """Find the +1 button that appears at 0:59"""
        try:
            # Check if we should refresh
            current_time = time.time()
            should_refresh = False
            
            if self.stealth_mode:
                # Refresh randomly every 30-90 seconds
                if current_time - self.last_refresh > random.randint(30, 90):
                    should_refresh = True
            else:
                # Refresh every 30 seconds
                if current_time - self.last_refresh > 30:
                    should_refresh = True
            
            if should_refresh:
                logger.info("🔄 Refreshing page...")
                self.driver.refresh()
                self.last_refresh = current_time
                self.human_delay(2, 4)
                
                # Random activity after refresh
                if self.stealth_mode:
                    self.random_mouse_movement()
            
            # Look for +1 button
            boost_selectors = [
                "//button[text()='+1']",  # Exact match
                "//button[contains(text(), '+1')]",
                "//button[.//*[text()='+1']]",
                "//button[contains(text(), 'Get your free RAM boost')]",
                "//a[contains(text(), 'Get your free RAM boost')]",
                "//button[@aria-label*='+1' or @aria-label*='boost']",
                "//button[contains(@class, 'boost')]"
            ]
            
            # Shuffle selectors for stealth
            if self.stealth_mode:
                random.shuffle(boost_selectors)
            
            for selector in boost_selectors:
                try:
                    wait_time = random.uniform(2, 4) if self.stealth_mode else 3
                    boost_btn = WebDriverWait(self.driver, wait_time).until(
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
        """Click the +1 button with human-like behavior"""
        try:
            logger.info("⚡ Clicking +1 button...")
            
            # Scroll to button
            self.driver.execute_script(
                "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", 
                button
            )
            
            self.human_delay(0.3, 0.8)
            
            if self.stealth_mode:
                # Human-like click with random offset
                actions = ActionChains(self.driver)
                actions.move_to_element_with_offset(
                    button,
                    random.randint(-8, 8),
                    random.randint(-8, 8)
                )
                actions.pause(random.uniform(0.1, 0.4))
                
                # Occasionally double-click like human mistake
                if random.random() > 0.9:
                    actions.double_click()
                    logger.info("👤 Human-like double click")
                else:
                    actions.click()
                
                actions.perform()
            else:
                # Direct JavaScript click
                self.driver.execute_script("arguments[0].click();", button)
            
            # Wait for action
            self.human_delay(1, 2)
            
            # Random activity after click
            if self.stealth_mode and random.random() > 0.5:
                self.random_mouse_movement()
                self.random_scroll()
            
            # Update stats
            self.total_clicks += 1
            self.last_click = datetime.now()
            self.consecutive_fails = 0
            
            # Check for success
            page_text = self.driver.page_source.lower()
            success_words = ['success', 'boost', 'activated', 'applied', 'increased']
            
            if any(word in page_text for word in success_words):
                logger.info("✅ +1 button clicked successfully!")
            else:
                logger.info("✅ Button clicked")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Click error: {e}")
            self.consecutive_fails += 1
            return False
    
    def check_server_status(self):
        """Check if server is online/offline"""
        try:
            status_selectors = [
                "//*[contains(text(), 'Online')]",
                "//*[contains(text(), 'Offline')]",
                "//*[contains(text(), 'Starting')]",
                "//*[contains(text(), 'Stopped')]",
                "//*[contains(@class, 'status-online')]",
                "//*[contains(@class, 'status-offline')]"
            ]
            
            for selector in status_selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    for elem in elements:
                        text = elem.text.strip()
                        if text and len(text) < 50:  # Avoid large text blocks
                            if 'Online' in text or 'Starting' in text:
                                logger.info(f"📊 Server status: {text}")
                                return 'online'
                            elif 'Offline' in text or 'Stopped' in text:
                                logger.info(f"📊 Server status: {text}")
                                return 'offline'
                except:
                    continue
            
            # Check for start/stop buttons
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
                    "//button[contains(@class, 'btn-start')]"
                ]
                
                for selector in start_selectors:
                    try:
                        start_btn = WebDriverWait(self.driver, 5).until(
                            EC.element_to_be_clickable((By.XPATH, selector))
                        )
                        if start_btn:
                            if self.stealth_mode:
                                actions = ActionChains(self.driver)
                                actions.move_to_element(start_btn)
                                actions.pause(0.2)
                                actions.click()
                                actions.perform()
                            else:
                                start_btn.click()
                            
                            logger.info("✅ Start button clicked, waiting...")
                            
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
        """Main monitoring loop to keep server alive"""
        logger.info("🚀 Starting 24/7 server keeper monitoring...")
        logger.info(f"🛡️ Stealth mode: {self.stealth_mode}")
        
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
            last_status_log = 0
            
            while self.is_running and self.consecutive_fails < self.max_fails:
                check_count += 1
                current_time = time.time()
                elapsed_minutes = (current_time - self.session_start.timestamp()) / 60
                
                # Log status every 10-20 checks or every 5 minutes
                if (check_count % random.randint(10, 20) == 0 or 
                    current_time - last_status_log > 300):
                    
                    last_status_log = current_time
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
                        # Wait after starting
                        self.human_delay(10, 20)
                        continue
                    else:
                        logger.error("❌ Failed to start server")
                        self.consecutive_fails += 1
                
                # Find shutdown timer
                timer = self.find_shutdown_timer()
                
                if timer:
                    # Check if timer is at critical point (0:59, 0:58, etc.)
                    if any(pattern in timer for pattern in ['0:59', '0:58', '0:57', '0:56']):
                        logger.info(f"🎯 CRITICAL TIMER: {timer}! Looking for +1 button...")
                        
                        # Look for +1 button
                        plus_one_btn = self.find_plus_one_button()
                        
                        if plus_one_btn:
                            # CLICK IT!
                            if self.click_plus_one_button(plus_one_btn):
                                logger.info(f"✅ +1 clicked! Timer should reset. Total clicks: {self.total_clicks}")
                                
                                # Wait for timer to reset
                                self.human_delay(5, 10)
                                
                                # Check if timer reset
                                new_timer = self.find_shutdown_timer()
                                if new_timer and '1:00' in new_timer:
                                    logger.info("🎉 Timer successfully reset to 1:00!")
                                elif new_timer:
                                    logger.info(f"🔄 Timer now at: {new_timer}")
                                else:
                                    logger.info("🔍 Timer no longer visible (should be reset)")
                            else:
                                logger.error("❌ Failed to click +1 button")
                                self.consecutive_fails += 1
                        else:
                            logger.info(f"⏳ Timer at {timer} but no +1 button yet")
                            
                            # Wait shorter if timer is critical
                            wait_time = random.randint(5, 15) if self.stealth_mode else 10
                            logger.info(f"⏳ Waiting {wait_time} seconds...")
                            time.sleep(wait_time)
                    else:
                        # Timer not critical, wait longer
                        if '1:00' in timer or '0:45' in timer or '0:30' in timer:
                            # Medium priority timers
                            wait_time = random.randint(15, 30) if self.stealth_mode else 20
                        else:
                            # Low priority timers
                            wait_time = random.randint(30, 60) if self.stealth_mode else 40
                        
                        logger.info(f"⏳ Timer at {timer}, waiting {wait_time} seconds...")
                        time.sleep(wait_time)
                else:
                    # No timer found, check for +1 button anyway
                    logger.info("🔍 No timer found, checking for +1 button...")
                    plus_one_btn = self.find_plus_one_button()
                    
                    if plus_one_btn:
                        logger.info("🎯 Found +1 button without timer!")
                        self.click_plus_one_button(plus_one_btn)
                    else:
                        # Wait random time
                        wait_time = random.randint(30, 90) if self.stealth_mode else 60
                        logger.info(f"🔍 Nothing found, waiting {wait_time} seconds...")
                        
                        # Do occasional activity during long waits
                        for i in range(3):
                            time.sleep(wait_time / 3)
                            if self.stealth_mode and random.random() > 0.7:
                                self.random_scroll()
                
                # Recovery check
                if self.consecutive_fails >= 3:
                    logger.warning(f"🔄 {self.consecutive_fails} consecutive fails, attempting recovery...")
                    
                    # Refresh and check status
                    self.driver.refresh()
                    self.last_refresh = time.time()
                    self.human_delay(3, 5)
                    
                    # Reset consecutive fails after recovery attempt
                    if self.consecutive_fails < 5:
                        self.consecutive_fails = 0
            
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


# Quick test function
def quick_test():
    """Quick test of the keeper"""
    keeper = Aternos24_7Keeper()
    return keeper.run()


if __name__ == "__main__":
    quick_test()
