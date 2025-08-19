from groq_client import GroqClient
import re
import json as _json
import time
class MindmapGenerator:
    def __init__(self, api_key: str, model="llama3-70b-8192"):
        self.llm = GroqClient(api_key=api_key, model=model)

    def extract_json(self, text):
        # Prefer JSON inside triple backticks (optionally labeled as json)
        codeblock = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
        if codeblock:
            return codeblock.group(1).strip()
        # Fallback: first {...} block
        match = re.search(r'({[\s\S]*})', text)
        if match:
            return match.group(1)
        return text  # fallback

    def generate_mindmap(self, text):
        prompt = (
            "Given the following textbook content, generate a mindmap as a JSON tree. "
            "Each node should have a 'title' and an optional 'children' array. "
            "Where relevant, include a 'text' field in nodes to provide important explanations, definitions, or summaries. "
            "Be comprehensive and detailed, not just brief titles. "
            "Focus on the main subject and its subtopics. Clearly identify and split subtopics. "
            "Ignore or skip activities, exercises, projects, 'Did you know', 'What you have learnt', summaries, trivia, and other non-essential or instructional sections. "
            "Ensure every node is a valid JSON object with a 'title' key. Output strict, valid JSON only. If you cannot output valid JSON, output nothing. "
            "Provide a concise but comprehensive structure of the chapter's concepts and how they are organized. "
            "Textbook content:\n"
            f"{text}\n"
            "Output only the JSON."
        )
        print(f"[DEBUG] LLM prompt: {prompt[:500]}..." if len(prompt) > 500 else f"[DEBUG] LLM prompt: {prompt}")
        response = self.llm.generate(prompt)
        print(f"[DEBUG] Raw LLM response: {response[:500]}..." if isinstance(response, str) and len(response) > 500 else f"[DEBUG] Raw LLM response: {response}")
        json_str = self.extract_json(response)
        print(f"[DEBUG] Extracted JSON: {json_str[:500]}..." if isinstance(json_str, str) and len(json_str) > 500 else f"[DEBUG] Extracted JSON: {json_str}")

        def try_fix_json(s):
            # Remove trailing commas
            s = re.sub(r',\s*([}\]])', r'\1', s)
            # Add missing commas between objects (very basic, not perfect)
            s = re.sub(r'}\s*{', '}, {', s)
            # Add missing commas between array elements (very basic)
            s = re.sub(r']\s*{', '], {', s)
            # Fix missing quotes around keys (risky, but can help)
            s = re.sub(r'([,{\[]\s*)([a-zA-Z0-9_]+)(\s*:)', r'\1"\2"\3', s)
            # Remove extraneous backticks or code block markers
            s = s.replace('```json', '').replace('```', '').strip()
            return s

        # Try up to 3 rounds of fixing
        for attempt in range(3):
            try:
                parsed = _json.loads(json_str)
                print(f"[DEBUG] JSON parsed successfully on attempt {attempt+1}")
                return _json.dumps(parsed, indent=2)
            except Exception as e:
                print(f"[ERROR] JSON parsing failed on attempt {attempt+1}: {e}")
                json_str = try_fix_json(json_str)
        print(f"[ERROR] All attempts to fix JSON failed. Returning error message.")
        raise ValueError("LLM did not return valid JSON, even after attempted fixes.")
    def summarize_text(self, text):
        prompt = (
            "Summarize the following textbook content in 2-3 sentences, focusing on the main ideas and key facts. "
            "Text:\n"
            f"{text}\n"
            "Summary:"
        )
        response = self.llm.generate(prompt)
        return response.strip()
    def hierarchical_summarize(self, texts, max_group_size=8, max_summary_length=3000):
        # Summarize each chunk
        summaries = []
        for i, text in enumerate(texts):
            print(f"[DEBUG] Summarizing chunk {i+1}/{len(texts)}")
            summaries.append(self.summarize_text(text))
            time.sleep(1)  # Throttle to avoid rate limits

        # Recursively summarize groups if too long
        while True:
            combined = "\n".join(summaries)
            if len(combined) < max_summary_length:
                return combined
            print(f"[DEBUG] Combined summary too long ({len(combined)} chars), summarizing in groups...")
            new_summaries = []
            for i in range(0, len(summaries), max_group_size):
                group = "\n".join(summaries[i:i+max_group_size])
                new_summaries.append(self.summarize_text(group))
                time.sleep(1)
            summaries = new_summaries