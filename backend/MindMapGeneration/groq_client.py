import time
import requests

class GroqClient:
    def __init__(self, api_key: str, model: str = "llama3-70b-8192"):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"

    def generate(self, prompt: str, max_retries=5):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.2,
            "max_tokens": 2048
        }
        for attempt in range(max_retries):
            try:
                print(f"[DEBUG] Sending prompt to Groq API: {prompt[:500]}..." if len(prompt) > 500 else f"[DEBUG] Sending prompt to Groq API: {prompt}")
                response = requests.post(self.base_url, headers=headers, json=data)
                print(f"[DEBUG] Groq API response status: {response.status_code}")
                print(f"[DEBUG] Groq API response JSON: {response.text[:500]}..." if len(response.text) > 500 else f"[DEBUG] Groq API response JSON: {response.text}")
                if response.status_code == 429:
                    # Parse the suggested wait time from the error message if available
                    try:
                        wait_time = 10  # Default wait time
                        resp_json = response.json()
                        msg = resp_json.get("error", {}).get("message", "")
                        import re
                        match = re.search(r"try again in ([0-9.]+)s", msg)
                        if match:
                            wait_time = float(match.group(1)) + 1  # Add a buffer
                        print(f"[WARN] Rate limit hit. Waiting {wait_time} seconds before retrying...")
                        time.sleep(wait_time)
                        continue
                    except Exception as e:
                        print(f"[ERROR] Could not parse wait time from 429 error: {e}")
                        time.sleep(10)
                        continue
                response.raise_for_status()
                return response.json()["choices"][0]["message"]["content"]
            except Exception as e:
                print(f"[ERROR] Exception in GroqClient.generate: {e}")
                if attempt == max_retries - 1:
                    import traceback
                    traceback.print_exc()
                    raise
                else:
                    print(f"[WARN] Retrying ({attempt+1}/{max_retries}) after error...")
                    time.sleep(5)