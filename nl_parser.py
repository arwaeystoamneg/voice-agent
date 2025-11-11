# nl_parser.py
import os
import json
from dotenv import load_dotenv
import openai
import re

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

SYSTEM_PROMPT = """
You are a translator that converts a single user instruction into a JSON action plan
for a browser automation agent. Return valid JSON only, no extra text.

Schema:
{
  "intent": "<string>",
  "steps": [ { "action": "<navigate|search|click_result|scroll|fill|press|compose_email>", ... } ],
  "confirm": <true|false>
}

Be concise. Examples:
User: "Search Google for Tesla stock and click the first result"
-> { "intent":"search_and_click", "steps":[{"action":"navigate","url":"https://www.google.com"},{"action":"search","query":"Tesla stock"},{"action":"click_result","which":1}], "confirm": false }

If the command references sending an email or anything destructive, set "confirm": true.
If uncertain, set intent "unknown" and leave steps empty.
"""

from openai import OpenAI
client = OpenAI()  

def parse(text: str) -> dict:
    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": text}
            ],
            temperature=0.0,
        )

        out = resp.choices[0].message.content.strip()

        try:
            return json.loads(out)
        except Exception:
            m = re.search(r"(\{.*\})", out, re.DOTALL)
            if m:
                try:
                    return json.loads(m.group(1))
                except Exception as e:
                    print("[nl_parser] JSON parse error:", e)
            return {"intent": "unknown", "steps": [], "confirm": False, "raw": out}

    except Exception as e:
        print("[nl_parser] LLM call failed:", e)
        return {"intent": "unknown", "steps": [], "confirm": False}