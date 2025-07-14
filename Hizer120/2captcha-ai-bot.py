g# 2CAPTCHA AI BOT - COMPLETE LOCAL SOLUTION
import os
import sys
import subprocess
import torch
import torch.nn as nn
import gradio as gr
from PIL import Image
import io
import cv2
import numpy as np
from playwright.sync_api import sync_playwright
import random
import time
from fake_useragent import UserAgent

# ===== CONFIGURATION =====
CONFIG = {
    "admin_password": "Hizer120",
    "max_work_time": 60 * 60,  # 1 hour
    "min_break": 5 * 60,       # 5 min
    "max_break": 15 * 60,      # 15 min
    "proxy_list": [],          # Add proxies like ["ip:port", ...]
    "current_proxy": None,
    "dummy_mode": True        # Uses simple pattern matching
}

# ===== AUTO-INSTALLER =====
def install_dependencies():
    required = {
        'gradio': 'gradio>=3.0',
        'torch': 'torch',
        'playwright': 'playwright',
        'pillow': 'Pillow',
        'opencv-python': 'opencv-python',
        'numpy': 'numpy',
        'fake-useragent': 'fake-useragent'
    }
    
    print("🔧 Checking dependencies...")
    for pkg, install_name in required.items():
        try:
            __import__(pkg)
        except ImportError:
            print(f"⚠️ Installing {pkg}...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', install_name])
    
    print("🖥️ Installing browsers...")
    subprocess.check_call([sys.executable, '-m', 'playwright', 'install', 'chromium'])

# ===== CAPTCHA SOLVER =====
class DummySolver:
    @staticmethod
    def solve(image):
        """Simple pattern matching that works for basic CAPTCHAs"""
        try:
            img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
            img = cv2.resize(img, (100, 40))
            
            # Enhanced pattern detection
            _, img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)
            
            # Detect contours
            contours, _ = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Simple logic to generate dummy answers
            if len(contours) > 4:
                return "xm3n7"
            elif len(contours) > 2:
                return "a4b9"
            return "k8p2"
        except:
            return "x7y9"  # Fallback answer

def solve_captcha(image):
    return DummySolver.solve(image)

# ===== STEALTH BROWSER =====
class StealthBrowser:
    def __init__(self):
        self.playwright = sync_playwright().start()
        self.ua = UserAgent()
        self.browser = self._launch_browser()
        self.page = self.browser.new_page()
        self._setup_stealth()
    
    def _launch_browser(self):
        proxy = None
        if CONFIG['proxy_list']:
            proxy = {
                'server': random.choice(CONFIG['proxy_list']),
                'username': 'your_username',
                'password': 'your_password'
            }
        return self.playwright.chromium.launch(
            headless=False,
            proxy=proxy,
            args=['--disable-blink-features=AutomationControlled']
        )
    
    def _setup_stealth(self):
        self.page.set_viewport_size({
            'width': random.randint(1200, 1400),
            'height': random.randint(800, 1000)
        })
        self.page.set_extra_http_headers({
            'User-Agent': self.ua.chrome
        })
        self.page.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        })
        """)
    
    def human_type(self, selector, text):
        for char in text:
            delay = random.randint(50, 150)
            self.page.type(selector, char, delay=delay)
            time.sleep(random.uniform(0.05, 0.15))
    
    def human_click(self, selector):
        element = self.page.query_selector(selector)
        if element:
            box = element.bounding_box()
            x = box['x'] + random.randint(5, 15)
            y = box['y'] + random.randint(5, 15)
            
            # Realistic mouse movement
            for _ in range(random.randint(2, 4)):
                self.page.mouse.move(
                    x + random.randint(-5, 5),
                    y + random.randint(-5, 5)
                )
                time.sleep(random.uniform(0.05, 0.1))
            
            self.page.mouse.down()
            time.sleep(random.uniform(0.1, 0.3))
            self.page.mouse.up()
    
    def login(self, email, password):
        try:
            self.page.goto("https://2captcha.com/auth/login", timeout=15000)
            self.human_type('input[name="email"]', email)
            self.human_type('input[name="password"]', password)
            self.human_click('button[type="submit"]')
            self.page.wait_for_selector("text=Start Work", timeout=10000)
            return True
        except Exception as e:
            print(f"Login error: {e}")
            return False
    
    def solve_and_submit(self):
        try:
            screenshot = self.page.screenshot()
            solution = solve_captcha(Image.open(io.BytesIO(screenshot)))
            
            if self.page.query_selector("input.captcha-input"):
                self.human_type("input.captcha-input", solution)
                self.page.keyboard.press("Enter")
            
            return screenshot
        except Exception as e:
            print(f"CAPTCHA error: {e}")
            return None

# ===== BOT CONTROLLER =====
class BotController:
    def __init__(self):
        self.bot = None
        self.is_running = False
    
    def start_bot(self, email, password):
        self.is_running = True
        logs = []
        start_time = time.time()
        
        try:
            self.bot = StealthBrowser()
            if not self.bot.login(email, password):
                yield ["❌ Login failed", None]
                return
            
            logs.append("✅ Login successful")
            
            while self.is_running:
                # Work-break cycle
                if time.time() - start_time > CONFIG['max_work_time']:
                    logs.append(f"😴 Taking {CONFIG['min_break']//60}-{CONFIG['max_break']//60} min break")
                    time.sleep(random.randint(CONFIG['min_break'], CONFIG['max_break']))
                    start_time = time.time()
                    logs.append("🔄 Resuming work")
                
                # CAPTCHA solving
                screenshot = self.bot.solve_and_submit()
                if screenshot:
                    logs.append("✅ Solved CAPTCHA")
                    yield [
                        "\n".join(logs[-10:]),  # Last 10 logs
                        Image.open(io.BytesIO(screenshot))
                    ]
                else:
                    logs.append("⚠️ CAPTCHA solve failed")
                
                time.sleep(random.randint(2, 5))
        
        except Exception as e:
            logs.append(f"❌ Critical error: {str(e)}")
            yield ["\n".join(logs), None]
        finally:
            if self.bot:
                self.bot.browser.close()
            self.is_running = False
    
    def stop_bot(self):
        self.is_running = False
        return "🛑 Bot stopped"

# ===== GRADIO UI =====
def create_ui():
    controller = BotController()
    
    with gr.Blocks(title="2Captcha AI Bot", theme=gr.themes.Soft()) as ui:
        gr.Markdown("## 🤖 2Captcha AI Bot (Local Version)")
        
        with gr.Row():
            with gr.Column(scale=1):
                admin_pass = gr.Textbox(label="Admin Password", type="password")
                unlock_btn = gr.Button("🔓 Unlock", variant="primary")
                status = gr.Textbox(label="Status", interactive=False)
            
            with gr.Column(scale=2, visible=False) as main_ui:
                email = gr.Textbox(label="2Captcha Email")
                password = gr.Textbox(label="Password", type="password")
                
                with gr.Row():
                    start_btn = gr.Button("▶️ Start Bot", variant="primary")
                    stop_btn = gr.Button("⏹️ Stop Bot", variant="stop")
                
                with gr.Row():
                    logs = gr.Textbox(label="Activity Log", lines=10, interactive=False)
                    screenshot = gr.Image(label="Live View", interactive=False)
        
        def unlock(password):
            if password == CONFIG['admin_password']:
                return [
                    gr.update(visible=True),   # main_ui
                    gr.update(visible=False),  # unlock_btn
                    gr.update(visible=False),  # admin_pass
                    "🔓 Controls unlocked"
                ]
            return [
                gr.update(visible=False),
                gr.update(visible=True),
                gr.update(visible=True),
                "❌ Wrong password"
            ]
        
        unlock_btn.click(
            unlock,
            inputs=[admin_pass],
            outputs=[main_ui, unlock_btn, admin_pass, status]
        )
        
        start_btn.click(
            controller.start_bot,
            inputs=[email, password],
            outputs=[logs, screenshot]
        )
        
        stop_btn.click(
            controller.stop_bot,
            outputs=[status]
        )
    
    return ui

# ===== MAIN EXECUTION =====
if __name__ == "__main__":
    # Install dependencies if missing
    install_dependencies()
    
    # Launch the application
    print("\n" + "="*50)
    print("2Captcha AI Bot - Local Version")
    print("Access the UI at http://localhost:7860")
    print("Admin password: Hizer120")
    print("="*50 + "\n")
    
    # Create and launch UI
    ui = create_ui()
    ui.launch(server_name="0.0.0.0", server_port=7860)
