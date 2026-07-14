# ==========================================================================
# R.H.E.A. - OS AUTOMATION & VISION CORE (STRICT EXECUTION)
# ==========================================================================

import pyautogui
from PIL import ImageGrab
import os
import time

class SystemController:
    def __init__(self):
        # Safety mechanism: Slam mouse to any corner to instantly abort RHEA's control
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.3 
        print("[SYSTEM] Automation Controller Initialized. PC Control Granted to R.H.E.A.")

    def get_mouse_position(self):
        return pyautogui.position()

    def take_vision_screenshot(self, save_path="vision_cache.png"):
        try:
            print("[R.H.E.A.] Capturing screen data...")
            screenshot = ImageGrab.grab()
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            full_path = os.path.join(base_dir, save_path)
            screenshot.save(full_path)
            return True, full_path
        except Exception as e:
            print(f"[ERROR] Vision capture failed: {e}")
            return False, str(e)

    def open_application(self, app_name):
        """
        [CMD: OPEN, app_name]
        Uses the Windows Start menu to instantly search and open any installed app.
        """
        try:
            print(f"[AUTOMATION] Launching: {app_name}")
            pyautogui.press('win')
            time.sleep(0.5) # Wait half a second for Start Menu to appear
            pyautogui.write(app_name, interval=0.03)
            time.sleep(0.5) # Wait half a second for Windows to find the app
            pyautogui.press('enter')
            return f"Successfully launched {app_name}."
        except pyautogui.FailSafeException:
            return "Action aborted. Boss triggered the physical failsafe."
        except Exception as e:
            return f"Failed to launch application: {e}"

    def type_text(self, text, press_enter=False):
        """
        [CMD: TYPE, text_to_type]
        Types exact strings into whatever input field is currently active.
        """
        try:
            print(f"[AUTOMATION] Typing text...")
            pyautogui.write(text, interval=0.02)
            if press_enter:
                pyautogui.press('enter')
            return "Text typed successfully."
        except pyautogui.FailSafeException:
            return "Action aborted. Boss triggered the physical failsafe."
        except Exception as e:
            return f"Failed to type text: {e}"

    def execute_shortcut(self, keys_list):
        """
        [CMD: HOTKEY, key1, key2]
        Executes keyboard shortcuts like 'ctrl, c' or 'alt, f4'.
        """
        try:
            print(f"[AUTOMATION] Executing shortcut: {' + '.join(keys_list)}")
            pyautogui.hotkey(*[k.strip().lower() for k in keys_list])
            return f"Executed shortcut: {', '.join(keys_list)}"
        except Exception as e:
            return f"Failed to execute shortcut: {e}"

    def move_and_click(self, x, y):
        """
        [CMD: CLICK, x, y]
        Moves the mouse to specific coordinates and clicks once.
        """
        try:
            print(f"[AUTOMATION] Moving and clicking at X:{x}, Y:{y}")
            # Moves smoothly so it doesn't look robotic/teleporting
            pyautogui.moveTo(x, y, duration=0.3, tween=pyautogui.easeInOutQuad)
            pyautogui.click()
            return f"Clicked successfully at coordinates {x}, {y}."
        except pyautogui.FailSafeException:
            return "Action aborted. Boss triggered the physical failsafe."
        except Exception as e:
            return f"Failed to click coordinates: {e}"

    def mouse_scroll(self, direction, amount):
        """
        [CMD: SCROLL, direction, amount]
        Scrolls the active window.
        """
        try:
            print(f"[AUTOMATION] Scrolling {direction} by {amount} units.")
            click_amount = int(amount) if direction.lower() == "up" else -int(amount)
            pyautogui.scroll(click_amount)
            return f"Scrolled {direction}."
        except Exception as e:
            return f"Scroll execution failed: {e}"