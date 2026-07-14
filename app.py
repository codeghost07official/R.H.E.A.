# ==========================================================================
# R.H.E.A. - MAIN APPLICATION CORE (ZERO-LATENCY PARSER)
# ==========================================================================

import webview
import time
import random
import os
import threading
import re
from datetime import datetime

from src.llm import LlamaEngine
from src.audio import AudioController
from src.automation import SystemController
from src.database import MemoryCore

MAIN_WINDOW = None
CURRENT_LANG = "en"
ENGINES = {}

class RheaAPI:
    def process_text_command(self, command):
        # Fire text prompts instantly into the background thread
        threading.Thread(target=unified_command_executor, args=(command,), daemon=True).start()
        return "BRIDGE_RECEIVED"


def unified_command_executor(command):
    global CURRENT_LANG, MAIN_WINDOW
    try:
        if not command.strip():
            return

        # 1. Check Memory Context
        context = ENGINES['memory'].recall_relevant_memory(command)

        # 2. Get LLM Raw Response (e.g., "Opening VS Code now, Boss. [CMD: OPEN, code]")
        raw_response = ENGINES['llm'].generate_response(command, context_memory=context)

        # 3. Isolate the dialogue from the machine tags
        extracted_commands = re.findall(r'\[CMD:\s*(.*?)\]', raw_response)
        clean_dialogue = re.sub(r'\[CMD:\s*.*?\]', '', raw_response).strip()

        # 4. Speak and log ONLY the clean dialogue (zero-latency single sentence)
        if clean_dialogue:
            threading.Thread(target=ENGINES['audio'].speak, args=(clean_dialogue, CURRENT_LANG), daemon=True).start()
            update_ui_logs(clean_dialogue)

        # 5. Execute Physical PC Actions via PyAutoGUI
        if extracted_commands:
            for cmd_str in extracted_commands:
                # Split the tag by commas and clean up white space
                parts = [p.strip() for p in cmd_str.split(',')]
                action_type = parts[0].upper()
                
                print(f"[EXECUTION QUEUE] -> {action_type}")
                
                if action_type == "OPEN" and len(parts) > 1:
                    res = ENGINES['sys_control'].open_application(parts[1])
                    update_ui_logs(f"[SYSTEM] {res}")
                    
                elif action_type == "TYPE" and len(parts) > 1:
                    # Re-join in case the typed text contained commas
                    text_content = ",".join(parts[1:])
                    res = ENGINES['sys_control'].type_text(text_content, press_enter=False)
                    update_ui_logs(f"[SYSTEM] {res}")
                    
                elif action_type == "HOTKEY" and len(parts) > 1:
                    res = ENGINES['sys_control'].execute_shortcut(parts[1:])
                    update_ui_logs(f"[SYSTEM] {res}")
                    
                elif action_type == "CLICK" and len(parts) > 2:
                    try:
                        res = ENGINES['sys_control'].move_and_click(int(parts[1]), int(parts[2]))
                        update_ui_logs(f"[SYSTEM] {res}")
                    except ValueError:
                        pass
                        
                elif action_type == "SCROLL" and len(parts) > 2:
                    res = ENGINES['sys_control'].mouse_scroll(parts[1], parts[2])
                    update_ui_logs(f"[SYSTEM] {res}")

        # 6. Memory Persistence
        if "my" in command.lower() or "i like" in command.lower() or "remember" in command.lower():
            ENGINES['memory'].remember_fact(command)

    except Exception as e:
        print(f"[ERROR] Engine routing fault: {e}")
        update_ui_logs(f"Pipeline Error: {e}")


def update_ui_logs(text):
    global MAIN_WINDOW
    if MAIN_WINDOW:
        safe_text = text.replace("'", "\\'").replace("\n", " ")
        MAIN_WINDOW.evaluate_js(f"addLog('{safe_text}', 'rhea');")
        MAIN_WINDOW.evaluate_js("updateStatus('AWAITING WAKE WORD');")


def background_tasks():
    global MAIN_WINDOW
    time.sleep(1)
    while True:
        try:
            if not MAIN_WINDOW:
                time.sleep(0.5)
                continue

            cpu_usage = random.randint(12, 32)
            ram_percent = random.randint(45, 52)
            ram_string = f"{round((ram_percent / 100) * 16, 1)} GB"

            now = datetime.now()
            current_time = now.strftime("%I:%M:%S %p")
            current_date = now.strftime("%d %b %Y")
            
            x, y = ENGINES['sys_control'].get_mouse_position()

            js_code = f"""
            updateTelemetry({cpu_usage}, '{ram_string}', {ram_percent});
            updateDateTime('{current_date}', '{current_time}');
            updateAutomationStatus({x}, {y}, 'ACTIVE');
            """
            MAIN_WINDOW.evaluate_js(js_code)
            time.sleep(1)
        except Exception as e:
            break


def voice_listening_loop():
    global CURRENT_LANG, MAIN_WINDOW
    time.sleep(3) 
    
    now = datetime.now().hour
    if now < 12: greeting = "Good morning"
    elif now < 18: greeting = "Good afternoon"
    else: greeting = "Good evening"
    
    ENGINES['audio'].speak(f"{greeting}, Boss. Systems fully online.", CURRENT_LANG)
    
    while True:
        try:
            if ENGINES['audio'].listen_for_wake_word():
                if MAIN_WINDOW:
                    MAIN_WINDOW.evaluate_js("updateStatus('LISTENING...');")
                
                command = ENGINES['audio'].listen(timeout=5, phrase_time_limit=10)
                
                if command:
                    if MAIN_WINDOW:
                        MAIN_WINDOW.evaluate_js(f"addLog('{command}', 'user');")
                        MAIN_WINDOW.evaluate_js("updateStatus('PROCESSING QUERY...');")
                    unified_command_executor(command)
                else:
                    if MAIN_WINDOW:
                        MAIN_WINDOW.evaluate_js("updateStatus('AWAITING WAKE WORD');")
        except Exception as e:
            time.sleep(2)


def main():
    print("[SYSTEM] Initializing R.H.E.A. Core...")
    global ENGINES, MAIN_WINDOW
    
    ENGINES['memory'] = MemoryCore()
    ENGINES['sys_control'] = SystemController()
    ENGINES['llm'] = LlamaEngine()
    ENGINES['audio'] = AudioController()
    
    api = RheaAPI()
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    html_path = os.path.join(current_dir, 'index.html')

    MAIN_WINDOW = webview.create_window(
        'R.H.E.A. AI Assistant', 
        url=html_path, 
        js_api=api, 
        width=1280, 
        height=720, 
        background_color='#050505',
        min_size=(1000, 600)
    )

    def start_threads(window):
        threading.Thread(target=background_tasks, daemon=True).start()
        threading.Thread(target=voice_listening_loop, daemon=True).start()

    print("[SYSTEM] Launching GUI...")
    webview.start(start_threads, MAIN_WINDOW, debug=False)

if __name__ == '__main__':
    main()