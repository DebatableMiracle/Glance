import subprocess
import os
from datetime import datetime

def take_screenshot():
    filename = f"screenshots/screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    os.makedirs("screenshots", exist_ok=True)

    try:
        subprocess.run(["gnome-screenshot", "-f", filename], check=True)
        return filename
    except:
        try:
            subprocess.run(["scrot", filename], check=True)
            return filename
        except:
            return None