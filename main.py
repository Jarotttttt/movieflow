import ctypes
try:
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('movieflow.app.1.0')
except Exception:
    pass
import time, re, requests, threading
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from concurrent.futures import ThreadPoolExecutor, as_completed

from ui.app_ui import AppUI

PASSWORD = "Rahasia123!"
UA       = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

_active_drivers = []
_drivers_lock = threading.Lock()

def close_all_drivers():
    with _drivers_lock:
        for d in _active_drivers[:]:
            try:
                d.quit()
            except:
                pass
        _active_drivers.clear()

# ── Email helpers ──
def get_guerrilla_email():
    try:
        r = requests.get("https://www.guerrillamail.com/ajax.php?f=get_email_address",
                         headers={"User-Agent": UA})
        d = r.json()
        return d.get("email_addr"), d.get("sid_token")
    except Exception:
        return None, None

def get_guerrilla_emails(sid_token):
    r = requests.get(
        f"https://www.guerrillamail.com/ajax.php?f=get_email_list&offset=0&sid_token={sid_token}",
        headers={"User-Agent": UA})
    return r.json().get("list", [])

def get_guerrilla_email_content(email_id, sid_token):
    r = requests.get(
        f"https://www.guerrillamail.com/ajax.php?f=fetch_email&email_id={email_id}&sid_token={sid_token}",
        headers={"User-Agent": UA})
    return r.json()

def get_verification_link(sid_token, timeout=120, stop_check=None):
    start = time.time()
    while time.time() - start < timeout:
        if stop_check and stop_check():
            return None
        for mail in get_guerrilla_emails(sid_token):
            content = get_guerrilla_email_content(mail.get("mail_id"), sid_token)
            body = content.get("mail_body") or content.get("mail_body_html") or ""
            m = re.search(r'(https?://[^\s"\'<>]+(?:activate|confirm|verify|verification)[^\s"\'<>]*)', body)
            if m:
                return m.group(1)
        if stop_check and stop_check():
            return None
        time.sleep(2)
    return None


def create_account(index, log_func, stop_check=None):
    driver = None
    try:
        opts = webdriver.ChromeOptions()
        opts.add_argument("--disable-blink-features=AutomationControlled")
        opts.add_argument("--disable-gpu")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--window-size=1280,720")
        opts.add_experimental_option("excludeSwitches", ["enable-automation"])
        svc = Service()

        driver = webdriver.Chrome(service=svc, options=opts)
        with _drivers_lock:
            _active_drivers.append(driver)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        email, sid = get_guerrilla_email()
        if not email:
            log_func(f"[{index}] Failed to get email")
            return
        log_func(f"[{index}] Email: {email}")

        def s(): return stop_check and stop_check()
        if s(): return

        driver.get("https://movieflow.ai/signup")
        wait = WebDriverWait(driver, 10)

        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email']"))).send_keys(email)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='password']"))).send_keys(PASSWORD)

        btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Sign Up')]")
        driver.execute_script("arguments[0].click();", btn)
        log_func(f"[{index}] Signup sent")

        link = get_verification_link(sid, stop_check=stop_check)
        if not link:
            if stop_check and stop_check():
                log_func(f"[{index}] Dihentikan")
            else:
                log_func(f"[{index}] No verification link")
            return
        if s(): return

        driver.get(link)
        time.sleep(3)
        url = driver.current_url
        if any(x in url for x in ["dashboard", "home", "app"]):
            log_func(f"[{index}] Auto-logged in")
        else:
            log_func(f"[{index}] Manual login...")
            if s(): return
            driver.get("https://movieflow.ai/login")
            time.sleep(2)
            if s(): return
            driver.find_element(By.ID, "email").send_keys(email)
            driver.find_element(By.CSS_SELECTOR, "input[type='password']").send_keys(PASSWORD)
            driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
            time.sleep(2)

        log_func(f"[{index}] Account ready - browser stays open")

    except Exception as e:
        log_func(f"[{index}] Error: {e}")
        if driver:
            try:
                driver.save_screenshot(f"error_{index}.png")
                driver.quit()
                with _drivers_lock:
                    if driver in _active_drivers:
                        _active_drivers.remove(driver)
            except:
                pass


class MovieFlowApp:
    def __init__(self):
        import customtkinter as ctk
        self.window = ctk.CTk()
        self.ui = AppUI(self.window, "Movie Flow", "v2.0", self._start, self._stop)
        self.running = False

    def _start(self):
        try:
            n = int(self.ui.count_var.get())
        except:
            n = 1
        self.running = True
        self.ui.start_btn.configure(state="disabled")
        self.ui.stop_btn.configure(state="normal")
        self.ui.status_text.set("running")
        self.ui.stat_target.configure(text=str(n))
        self.ui.stat_ok.configure(text="0")
        self.ui.stat_fail.configure(text="0")
        threading.Thread(target=self._run_parallel, args=(n,), daemon=True).start()

    def _stop(self):
        self.running = False
        self.ui.log("Menghentikan semua...")
        self.window.after(2000, self._force_close)

    def _force_close(self):
        close_all_drivers()
        self.ui.log("Semua browser ditutup")
        self._reset_ui("dihentikan")

    def _reset_ui(self, status):
        self.ui.start_btn.configure(state="normal")
        self.ui.stop_btn.configure(state="disabled")
        self.ui.status_text.set(status)

    def _run_parallel(self, n):
        s, f = 0, 0

        def log_wrapper(idx, m):
            self.window.after(0, self.ui.log, f"[{idx}] {m}")

        with ThreadPoolExecutor(max_workers=n) as ex:
            futures = {}
            for i in range(1, n + 1):
                futures[ex.submit(create_account, i,
                                  lambda idx=i, m="": log_wrapper(idx, m),
                                  stop_check=lambda: not self.running)] = i

            for fut in as_completed(futures):
                r = fut.result()
                if r:
                    s += 1
                else:
                    f += 1
                self.window.after(0, lambda ok=s, fl=f: (
                    self.ui.stat_ok.configure(text=str(ok)),
                    self.ui.stat_fail.configure(text=str(fl)),
                ))

        self.running = False
        self.window.after(0, lambda: self._reset_ui("selesai"))
        self.window.after(0, lambda: self.ui.log("Selesai"))

    def run(self):
        self.window.mainloop()


if __name__ == "__main__":
    MovieFlowApp().run()

