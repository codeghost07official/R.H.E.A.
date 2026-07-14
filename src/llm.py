# ==========================================================================
# R.H.E.A. - CORE LLM ENGINE (LLAMA 3 / OLLAMA)
# ==========================================================================

import ollama
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

class LlamaEngine:
    def __init__(self):
        # Default to llama3 if not specified in .env
        self.model = os.getenv("OLLAMA_MODEL", "llama3")
        self.system_prompt = self._load_system_prompt()
        
        # Initialize conversation history with the system prompt to set her personality
        self.history = [{"role": "system", "content": self.system_prompt}]
        print(f"[SYSTEM] Llama Engine initialized with model: {self.model}")

    def _load_system_prompt(self):
        """
        Loads R.H.E.A.'s personality and user profile from the text file.
        """
        try:
            # Go up one directory from src/ to the root folder to find the file
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            prompt_path = os.path.join(base_dir, 'system_prompts.txt')
            
            with open(prompt_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            print(f"[WARNING] Could not load system_prompts.txt. Using default personality. Error: {e}")
            return "You are R.H.E.A., a highly intelligent, witty, and sarcastic AI assistant created by Jai."

    def generate_response(self, user_input, context_memory=""):
        """
        Sends the user's input to Llama 3 and returns the response.
        In the future, context_memory will contain RAG data from MySQL.
        """
        # If RAG database provides relevant memory, secretly inject it into the prompt
        if context_memory:
            augmented_prompt = f"[DATABASE MEMORY CONTEXT: {context_memory}]\n\nBoss says: {user_input}"
        else:
            augmented_prompt = user_input

        # Add the user's input to the conversation history
        self.history.append({"role": "user", "content": augmented_prompt})

        try:
            # Call local Ollama API
            response = ollama.chat(model=self.model, messages=self.history)
            reply = response['message']['content']
            
            # Append her reply to the history so she remembers the context of the conversation
            self.history.append({"role": "assistant", "content": reply})
            
            # Memory Management: Keep history from getting too large (limits context window crashes)
            # We keep the first message (System Prompt) and the last 20 interactions.
            if len(self.history) > 21:
                self.history = [self.history[0]] + self.history[-20:]

            return reply
            
        except Exception as e:
            error_msg = f"My neural link to Llama 3 is experiencing turbulence. Error: {e}"
            print(f"[ERROR] LLM Engine Failure: {error_msg}")
            
            # Usually happens if Ollama isn't running in the background
            if "Connection" in str(e):
                return "Boss, I can't reach my brain. Please make sure the Ollama app is running locally."
            
            return error_msg