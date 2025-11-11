# run_agent.py
import os
import time
import json
from dotenv import load_dotenv
from speech_manager import record_audio
from nl_parser import parse
from browser_agent import BrowserAgent
import openai

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

from openai import OpenAI

def transcribe_with_openai(file_path: str) -> str:
    """Transcribe audio using the new OpenAI API client (>=1.0.0)."""
    try:
        client = OpenAI() 
        with open(file_path, "rb") as f:
            resp = client.audio.transcriptions.create(
                model="whisper-1",
                file=f
            )
        text = resp.text.strip()
        print("[transcribe] ->", text)
        return text
    except Exception as e:
        print("[transcribe] failed:", e)
        return ""

def execute_plan(plan: dict, browser: BrowserAgent):
    intent = plan.get("intent", "")
    steps = plan.get("steps", [])
    for step in steps:
        action = step.get("action")
        if action == "navigate":
            url = step.get("url")
            browser.navigate(url)
        elif action == "search":
            q = step.get("query")
            browser.search_google(q)
        elif action == "click_result":
            which = step.get("which", 1)
            ok = browser.click_result(int(which))
            if not ok:
                print("I couldn't find that result. How should I proceed?")
        elif action == "scroll":
            amount = step.get("amount", "down")
            browser.scroll(amount)
        elif action == "fill":
            selector = step.get("selector")
            text = step.get("text", "")
            browser.fill(selector, text)
        elif action == "press":
            key = step.get("key", "Enter")
            browser.press(key)
        elif action == "compose_email":
            to = step.get("to")
            subject = step.get("subject", "")
            body = step.get("body", "")
            ok = browser.compose_email_gmail(to, subject, body)
            if not ok:
                print("I couldn't compose the email automatically; you'll need to complete it manually.")
        else:
            print(f"I don't know how to perform action {action}")

def main_loop():
    print("Voice browser agent — push-to-talk demo.")
    print("Press Enter to record (4s), Ctrl+C to exit.")
    browser = BrowserAgent(headful=True)
    try:
        while True:
            input("Press Enter to record a command...")
            try:
                wav = record_audio(duration=4)
            except Exception as e:
                print("audio recording failed:", e)
                continue
            txt = transcribe_with_openai(wav)
            if not txt:
                print("Sorry, I couldn't transcribe that. Try again.")
                continue
            print(f"I heard: {txt}")
            plan = parse(txt)
            print("[plan]", json.dumps(plan, indent=2))
            if plan.get("confirm", False):
                print("This action requires confirmation. Do you want me to proceed? Say yes or no.")
                cfile = record_audio(duration=3)
                cresp = transcribe_with_openai(cfile).lower()
                if "y" not in cresp and "yes" not in cresp:
                    print("Okay, cancelled.")
                    continue
            try:
                execute_plan(plan, browser)
            except Exception as e:
                print("execute_plan failed:", e)
                browser.close()
                browser = BrowserAgent(headful=True)
                continue
            print("Done. Ready for the next command.")
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        browser.close()

if __name__ == "__main__":
    main_loop()
