# browser_agent.py
import time
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

class BrowserAgent:
    def __init__(self, headful=True):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=not headful)
        self.page = self.browser.new_page()
        self.last_search_query = None
        self.last_results = [] 

    def close(self):
        try:
            self.browser.close()
        finally:
            self.playwright.stop()

    def navigate(self, url: str):
        if not url.startswith("http"):
            url = "https://" + url
        print("[browser] navigating to", url)
        self.page.goto(url, timeout=30000)
        time.sleep(1)

    def search_google(self, query: str):
        print("[browser] searching Google:", query)
        self.navigate("https://www.google.com")
        try:
            self.page.fill("input[name=q]", query, timeout=5000)
            self.page.keyboard.press("Enter")
            time.sleep(2)
        except PlaywrightTimeoutError:
            print("[browser] Google search selectors not found; trying URL search")
            self.navigate(f"https://www.google.com/search?q={query.replace(' ', '+')}")
        self.last_search_query = query
        self._scrape_results()

    def _scrape_results(self):
        try:
            results = self.page.query_selector_all("div#search a")
            self.last_results = []
            for r in results[:10]:
                href = r.get_attribute("href")
                text = r.inner_text()[:200]
                self.last_results.append({"href": href, "text": text})
            print("[browser] scraped", len(self.last_results), "results")
        except Exception:
            self.last_results = []

    def click_result(self, which: int):
        idx = max(1, which) - 1
        if idx < len(self.last_results):
            href = self.last_results[idx].get("href")
            print(f"[browser] clicking result #{which}: {href}")
            try:
                anchors = self.page.query_selector_all("div#search a")
                if idx < len(anchors):
                    anchors[idx].click()
                else:
                    self.navigate(href)
                time.sleep(1)
                return True
            except Exception as e:
                print("[browser] click failed:", e)
                return False
        else:
            print("[browser] requested result index out of range")
            return False

    def scroll(self, amount="down"):
        print("[browser] scrolling", amount)
        if amount == "down":
            self.page.keyboard.press("PageDown")
        elif amount == "up":
            self.page.keyboard.press("PageUp")
        else:
            try:
                n = int(amount)
                for _ in range(n):
                    self.page.keyboard.press("PageDown")
                    time.sleep(0.2)
            except Exception:
                self.page.keyboard.press("PageDown")
        time.sleep(0.5)

    def fill(self, selector: str, text: str):
        try:
            self.page.fill(selector, text, timeout=5000)
            time.sleep(0.3)
            return True
        except Exception as e:
            print("[browser] fill failed:", e)
            return False

    def press(self, key: str):
        self.page.keyboard.press(key)

    def compose_email_gmail(self, to: str, subject: str, body: str):
        print("[browser] compose email (Gmail) demo - fragile")
        self.navigate("https://mail.google.com/")
        time.sleep(3)
        try:
            self.page.click("div.T-I.T-I-KE.L3", timeout=5000)
            time.sleep(1)
            self.page.fill("textarea[name=to]", to, timeout=5000)
            self.page.fill("input[name=subjectbox]", subject, timeout=5000)
            self.page.fill("div[aria-label='Message Body']", body, timeout=5000)
            time.sleep(0.5)
            return True
        except Exception as e:
            print("[browser] compose email failed:", e)
            return False
