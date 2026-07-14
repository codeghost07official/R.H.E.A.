# ==========================================================================
# R.H.E.A. - CORE LLM ENGINE (STRICT LATENCY & MACRO CONTROL)
# ==========================================================================

import ollama
import os
from dotenv import load_dotenv

load_dotenv()

AGENT_MACRO_RULES = """

[CRITICAL SYSTEM OVERRIDES - YOU MUST OBEY THESE STRICTLY]

1. ZERO-LATENCY VOICE RULE: You are a voice assistant. You MUST limit your spoken response to EXACTLY ONE short, witty sentence (under 15 words). NO exceptions. NO long paragraphs.
2. PC AUTOMATION RULE: To control the PC, you MUST append a machine-readable tag at the absolute END of your short sentence. 

VALID COMMAND TAGS (Use exact formatting):
- Launch/Open an app: [CMD: OPEN, app_name]
- Type text: [CMD: TYPE, text_to_type]
- Execute shortcut: [CMD: HOTKEY, key1, key2]
- Click coordinates: [CMD: CLICK, x, y]
- Scroll: [CMD: SCROLL, up/down, amount]

PERFECT EXAMPLES:
User: "Open VS Code."
R.H.E.A.: Firing up your coding matrix now, Boss. [CMD: OPEN, code]

User: "Type print hello world."
R.H.E.A.: Injecting the text now. [CMD: TYPE, print('hello world')]
"""

class LlamaEngine:
    def __init__(self):
        self.model = os.getenv("OLLAMA_MODEL", "llama3")
        base_prompt = self._load_system_prompt()
        
        # Lock in the aggressive formatting and latency rules
        self.system_prompt = base_prompt + AGENT_MACRO_RULES
        self.history = [{"role": "system", "content": self.system_prompt}]
        print(f"[SYSTEM] Agentic Macro Llama Engine initialized using model: {self.model}")

    def _load_system_prompt(self):
        try:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            prompt_path = os.path.join(base_dir, 'system_prompts.txt')
            with open(prompt_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            return "You are R.H.E.A., a highly intelligent, witty, and sarcastic AI assistant."

    def generate_response(self, user_input, context_memory=""):
        if context_memory:
            augmented_prompt = f"[DATABASE MEMORY CONTEXT: {context_memory}]\n\nBoss says: {user_input}"
        else:
            augmented_prompt = user_input

        self.history.append({"role": "user", "content": augmented_prompt})

        try:
            response = ollama.chat(model=self.model, messages=self.history)
            reply = response['message']['content']
            
            self.history.append({"role": "assistant", "content": reply})
            
            if len(self.history) > 21:
                self.history = [self.history[0]] + self.history[-20:]

            return reply
        except Exception as e:
            print(f"[ERROR] LLM Query Intercept fault: {e}")
            return "My thought processors hit a wall. Let me try that again."