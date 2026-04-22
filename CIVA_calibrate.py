
import winsound
import time
import ctypes
from pynput import mouse
# from pynput.mouse import Button, Controller

# --- CHECK FOR ADMIN RIGHTS ---
def is_admin():
    try: 
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception: 
        return False

#if not  is_admin():           
#     print("ERROR: You MUST run this script as ADMINISTRATOR for MSFS control")
#     input("Press Enter to exit...")
#     exit()

# --- MACRO TEMPLATES ---
TEMPLATES = {
    "header": "<#> {name}",
    "move": "<mm>({x},{y},{wait})<#> {name}",
    "click_down": "<mlbd><#>",
    "click_up": "<mlbu><#>",
    "scroll_f": "<mwheel_f><#>",
    "scroll_b": "<mwheel_b><#>",
    "wait": "<wx>({wait},0)<#>"
}

BUTTONS = [
    {"name": "clear", "prompt": "Click on CLEAR"},
    {"name": "wy pt chg", "prompt": "Click on WY PT CHG"},
    {"name": "hold", "prompt": "Click on HOLD"},
    {"name": "remote", "prompt": "Click on REMOTE"},
    {"name": "insert", "prompt": "Click on INSERT"},
    {"name": "waypoint selector", "prompt": "Click on WAYPOINT SELECTOR"},
    {"name": "data selector", "prompt": "Click on DATA SELECTOR (Ensure it is on 'TEST')"},
    {"name": "0", "prompt": "Click on 0"}, {"name": "1", "prompt": "Click on 1"},
    {"name": "2", "prompt": "Click on 2"}, {"name": "3", "prompt": "Click on 3"},
    {"name": "4", "prompt": "Click on 4"}, {"name": "5", "prompt": "Click on 5"},
    {"name": "6", "prompt": "Click on 6"}, {"name": "7", "prompt": "Click on 7"},
    {"name": "8", "prompt": "Click on 8"}, {"name": "9", "prompt": "Click on 9"}
]

DIAL_POSITIONS = ["TK/GS", "HDG DA", "XTK TKE", "POS", "WAY PT", "DIS/TIME", "WIND", "DSRTK/STS", "TEST"]

class CalibrationWizard:
    def __init__(self):
        self.recorded_lines = []
        self.last_pos = (0, 0)
        self.event_captured = False
        self.global_wait = "200"
        #Keep at 300
        self.global_slow_wait = "300"           
        self.data_selector_coords = None

    def beep(self, freq=1000, dur=100):
        winsound.Beep(freq, dur)

    def on_click(self, x, y, button, pressed):
        if pressed and button == mouse.Button.left:
            self.last_pos = (int(x), int(y))
            self.event_captured = True
            return False

    def add_standard_action(self, action_key):
        self.recorded_lines.append(TEMPLATES[action_key])
        self.recorded_lines.append(TEMPLATES["wait"].format(wait=self.global_wait))

    def add_delayed_action(self, action_key):
        self.recorded_lines.append(TEMPLATES[action_key])
        self.recorded_lines.append(TEMPLATES["wait"].format(wait=self.global_slow_wait))

    def run(self):
        print("--- CIVA Calibration Assistant ---")
        self.global_wait = input("Enter global wait time (ms) [default 200]: ") or "200"
        
        for btn in BUTTONS:
            print(f" -> {btn['prompt']}...")
            self.event_captured = False
            with mouse.Listener(on_click=self.on_click) as _:
                while not self.event_captured:
                    time.sleep(0.1)
            
            x, y = self.last_pos
            if btn['name'] == "data selector": 
                self.data_selector_coords = (x, y)
                # print(f"   [DEBUG] Captured Data Selector at: {x}, {y}")
            
            self.beep()
            self.recorded_lines.append(TEMPLATES["header"].format(name=btn['name']))

            
            if "selector" in btn['name']:
                self.recorded_lines.append(TEMPLATES["move"].format(x=x, y=y, wait=self.global_slow_wait, name=btn['name']))
                self.add_delayed_action("click_down")
                self.add_delayed_action("click_up")
                self.add_delayed_action("scroll_f")
                self.add_delayed_action("click_down")
                self.add_delayed_action("click_up")
            else:
                self.recorded_lines.append(TEMPLATES["move"].format(x=x, y=y, wait=self.global_wait, name=btn['name']))
                self.add_standard_action("click_down")
                self.add_standard_action("click_up")
            self.recorded_lines.append("")

        doDataSelector = False
        if not doDataSelector:
            ans = input("\nSave output to CIVAinsCalibration.txt? (y/n): ")
            if ans.lower() == 'y': 
                self.save_file()          
        else:
            self.verify_data_selector()

    def verify_data_selector(self):
        if not self.data_selector_coords:
            print("\n[ERROR] Coordinates missing.")
            return
        
        input("\nPress Enter to begin (Tab to MSFS and DONT TOUCH MOUSE)...")
        for i in range(5, 0, -1):
            print(f"  {i}...")
            time.sleep(1)

        # DIRECT WINDOWS API CALL FOR ABSOLUTE POSITION
        x, y = self.data_selector_coords
        ctypes.windll.user32.SetCursorPos(x, y)
        print(f"  Sent cursor to Absolute: {x}, {y}")
        time.sleep(2.0) 

        # Re-verify position with pynput to see if it stayed there
        m = mouse.Controller()
        actual_x, actual_y = m.position
        print(f"  Sim reported cursor at: {actual_x}, {actual_y}")

        # FOCUS CLICK
        m.press(mouse.Button.left)
        time.sleep(0.2)
        m.release(mouse.Button.left)
        time.sleep(0.5)

        # DATA SELECTOR LOGIC (8 LEFT, 4 RIGHT)
        print("  Resetting to TK/GS...")
        for _ in range(8):
            m.scroll(0, -1)
            time.sleep(0.4)
        
        for pos in DIAL_POSITIONS:
            print(f"  Pos: {pos}")
            self.beep(800, 100)
            time.sleep(0.8)
            if pos != "TEST": 
                m.scroll(0, 1)

        print("  Returning to WAY PT...")
        for _ in range(4):
            m.scroll(0, -1)
            time.sleep(0.4)

        ans = input("\nVerified? (y/n): ")
        if ans.lower() == 'y': 
            self.save_file()


    def save_file(self):
        with open("CIVAinsCalibration.txt", "w") as f:
            f.write("\n".join(self.recorded_lines))
        print("\nSUCCESS!")

if __name__ == "__main__":
    wizard = CalibrationWizard()
    wizard.run()
