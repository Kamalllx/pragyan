import requests

class OllamaClient:
    def __init__(self, base_url="http://localhost:11434/api/generate", model="llama3"):
        self.base_url = base_url
        self.model = model

    def generate(self, prompt):
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }
        response = requests.post(self.base_url, json=payload)
        response.raise_for_status()
        return response.json()["response"]