# ==========================================================================
# R.H.E.A. - MAIN APPLICATION CORE
# ==========================================================================

import webview
import time
import random
import os
import threading
from datetime import datetime

# IMPORTING OUR CUSTOM BRAIN MODULES
from src.llm import LlamaEngine
from src.audio import AudioController
from src.automation import SystemController
from src.database import MemoryCore

class RheaAPI:
    """
    The main bridge connecting the UI, the Voice Engine, the LLM, and the PC.
    """
    def __init__(self):
        print("[SYSTEM] Booting Backend Modules... Please wait.")
        self.window = None
        
        # Initialize Core Modules
        self.memory = MemoryCore()
        self.sys_control = SystemController()
        self.llm = LlamaEngine()
        self.audio = AudioController()
        
        self.current_lang = "en"

    def set_window(self, window):
        self.window = window

    def process_text_command(self, command):
        """
        Handles commands coming from BOTH the UI text box and the Voice STT.
        """
        print(f"[BACKEND LOG] Received command: {command}")

        # 1. CHECK FOR OS AUTOMATION COMMANDS FIRST
        if command.lower().startswith("type "):
            text_to_type = command[5:]
            self.audio.speak("Typing that out now, Boss.", self.current_lang)
            res = self.sys_control.type_text(text_to_type, press_enter=True)
            return res

        if "take a screenshot" in command.lower():
            self.audio.speak("Capturing screen data.", self.current_lang)
            success, path = self.sys_control.take_vision_screenshot()
            return "Screenshot saved to vision cache." if success else "Screenshot failed."

        if "switch to hindi" in command.lower():
            self.current_lang = "hi"
            msg = "Language protocols updated. Main ab hindi mein baat karungi, Boss."
            self.audio.speak(msg, self.current_lang)
            return msg
            
        if "switch to english" in command.lower():
            self.current_lang = "en"
            msg = "Language protocols updated to British English, Boss."
            self.audio.speak(msg, self.current_lang)
            return msg

        # 2. RAG MEMORY RETRIEVAL
        context = self.memory.recall_relevant_memory(command)

        # 3. LLM GENERATION
        response = self.llm.generate_response(command, context_memory=context)

        # 4. MEMORY STORAGE (Save important facts automatically)
        if "my" in command.lower() or "i like" in command.lower() or "remember" in command.lower():
            self.memory.remember_fact(command)

        # 5. SPEAK RESPONSE (In a separate thread so UI doesn't freeze)
        threading.Thread(target=self.audio.speak, args=(response, self.current_lang), daemon=True).start()

        return response

def background_tasks(window, api):
    """Pushes telemetry and live clock data to the UI."""
    time.sleep(1)
    while True:
        try:
            # Simulate CPU/RAM
            cpu_usage = random.randint(10, 45)
            ram_percent = random.randint(30, 60)
            ram_string = f"{round((ram_percent / 100) * 16, 1)} GB"

            # Get Live Date and Time
            now = datetime.now()
            current_time = now.strftime("%I:%M:%S %p")
            current_date = now.strftime("%d %b %Y")
            
            # Get actual mouse position from PyAutoGUI
            x, y = api.sys_control.get_mouse_position()

            js_code = f"""
            updateTelemetry({cpu_usage}, '{ram_string}', {ram_percent});
            updateDateTime('{current_date}', '{current_time}');
            updateAutomationStatus({x}, {y}, 'ACTIVE');
            """
            
            window.evaluate_js(js_code)
            time.sleep(1)
        except Exception as e:
            break

def voice_listening_loop(window, api):
    """Background thread that constantly listens for the wake word ('riya')."""
    time.sleep(5) # Give the system time to fully boot and greet before listening
    
    # Optional: Initial greeting when app opens
    now = datetime.now().hour
    if now < 12: greeting = "Good morning"
    elif now < 18: greeting = "Good afternoon"
    else: greeting = "Good evening"
    
    api.audio.speak(f"{greeting}, Boss. R.H.E.A. core systems are online and ready.", api.current_lang)
    
    while True:
        try:
            if api.audio.listen_for_wake_word():
                # Wake word detected! Update UI
                window.evaluate_js("updateStatus('LISTENING...');")
                
                # Listen for the actual command
                command = api.audio.listen(timeout=5, phrase_time_limit=10)
                
                if command:
                    # Send command to UI
                    window.evaluate_js(f"addLog('{command}', 'user');")
                    window.evaluate_js("updateStatus('PROCESSING QUERY...');")
                    
                    # Process the command
                    response = api.process_text_command(command)
                    
                    # Send response back to UI
                    # Escape quotes to prevent JS errors
                    safe_response = response.replace("'", "\\'").replace("\n", " ")
                    window.evaluate_js(f"addLog('[R.H.E.A.] {safe_response}', 'rhea');")
                    window.evaluate_js("updateStatus('AWAITING WAKE WORD');")
                else:
                    window.evaluate_js("updateStatus('AWAITING WAKE WORD');")
        except Exception as e:
            print(f"[ERROR] Voice Loop crashed: {e}")
            time.sleep(2)

def main():
    print("[SYSTEM] Initializing R.H.E.A. Core...")
    api = RheaAPI()
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    html_path = os.path.join(current_dir, 'index.html')

    window = webview.create_window(
        'R.H.E.A. AI Assistant', 
        url=html_path, 
        js_api=api, 
        width=1280, 
        height=720, 
        background_color='#050505',
        min_size=(1000, 600)
    )
    api.set_window(window)

    def start_threads(window):
        # Start Telemetry thread
        threading.Thread(target=background_tasks, args=(window, api), daemon=True).start()
        # Start Voice Engine thread
        threading.Thread(target=voice_listening_loop, args=(window, api), daemon=True).start()

    print("[SYSTEM] Launching GUI...")
    webview.start(start_threads, window, debug=True)

if __name__ == '__main__':
    main()