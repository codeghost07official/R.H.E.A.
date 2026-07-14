# ==========================================================================
# R.H.E.A. - OS AUTOMATION & VISION CORE
# ==========================================================================

import pyautogui
from PIL import ImageGrab
import os
import time

class SystemController:
    def __init__(self):
        # PyAutoGUI Safety Settings
        # Moving the mouse manually to any corner of the screen aborts her control
        pyautogui.FAILSAFE = True
        
        # Add a tiny delay between actions to make her movements more human and less erratic
        pyautogui.PAUSE = 0.5 
        print("[SYSTEM] Automation Controller Initialized. PC Control Granted to R.H.E.A.")

    def get_mouse_position(self):
        """
        Returns the current X, Y coordinates of the mouse pointer.
        Used for UI telemetry in the dashboard.
        """
        return pyautogui.position()

    def take_vision_screenshot(self, save_path="vision_cache.png"):
        """
        Takes a screenshot of the primary monitor so R.H.E.A. can 'see'.
        Saves it locally to be analyzed by the LLM's vision capabilities later.
        """
        try:
            print("[R.H.E.A.] Capturing screen data...")
            screenshot = ImageGrab.grab()
            
            # Save the image to the root directory
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            full_path = os.path.join(base_dir, save_path)
            
            screenshot.save(full_path)
            return True, full_path
            
        except Exception as e:
            print(f"[ERROR] Vision capture failed: {e}")
            return False, str(e)

    def move_and_click(self, x, y, button="left"):
        """
        Smoothly moves the mouse to specific coordinates and clicks.
        """
        try:
            print(f"[R.H.E.A.] Moving cursor to {x}, {y}...")
            # duration and tween make the mouse glide smoothly rather than teleporting
            pyautogui.moveTo(x, y, duration=0.5, tween=pyautogui.easeInOutQuad)
            pyautogui.click(button=button)
            return f"Successfully clicked at {x}, {y}."
            
        except pyautogui.FailSafeException:
            print("[SYSTEM] FAILSAFE TRIGGERED BY BOSS.")
            return "Action aborted. Boss triggered the failsafe."
        except Exception as e:
            return f"Failed to execute click: {e}"

    def type_text(self, text, press_enter=False):
        """
        Types out the given text string on the keyboard.
        """
        try:
            print(f"[R.H.E.A.] Typing input...")
            # interval makes her type like a human rather than pasting instantly
            pyautogui.write(text, interval=0.03)
            
            if press_enter:
                pyautogui.press('enter')
                
            return f"Successfully typed text."
            
        except pyautogui.FailSafeException:
            print("[SYSTEM] FAILSAFE TRIGGERED BY BOSS.")
            return "Action aborted. Boss triggered the failsafe."

    def execute_shortcut(self, *keys):
        """
        Executes a keyboard shortcut (e.g., 'ctrl', 'c' or 'win', 'r').
        """
        try:
            print(f"[R.H.E.A.] Executing shortcut: {' + '.join(keys)}")
            pyautogui.hotkey(*keys)
            return f"Executed shortcut: {' + '.join(keys)}"
            
        except Exception as e:
            return f"Failed to execute shortcut: {e}"