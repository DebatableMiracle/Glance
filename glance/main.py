import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt, QTimer
from glance.gui import FloatingWidget
from glance.tray import SystemTray

class MainApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)
        
        # Create window
        self.window = FloatingWidget()
        
        # Create system tray
        self.tray = SystemTray(self.window)
        self.tray.tray_icon.show()
        
        # Position window after creating but before showing
        self.position_window()
        self.window.show()
        
        # Ensure window stays on top
        self.window.raise_()
        self.window.activateWindow()
    
    def position_window(self):
        # Get screen geometry
        screen = self.app.primaryScreen().availableGeometry()
        
        # Set window size
        self.window.resize(400, 600)
        
        # Calculate position (bottom right with 20px margin)
        x = screen.width() - self.window.width() - 20
        y = screen.height() - self.window.height() - 40  # Added more margin for taskbar
        
        # Move window
        self.window.move(x, y)
        
        # Schedule a position check after window is shown
        QTimer.singleShot(100, self.check_position)
    
    def check_position(self):
        # Get screen geometry
        screen = self.app.primaryScreen().availableGeometry()
        
        # Get current window position
        current_pos = self.window.pos()
        
        # Calculate expected position
        expected_x = screen.width() - self.window.width() - 20
        expected_y = screen.height() - self.window.height() - 40
        
        # If position is off, correct it
        if current_pos.x() != expected_x or current_pos.y() != expected_y:
            self.window.move(expected_x, expected_y)
            self.window.raise_()
            self.window.activateWindow()
    
    def run(self):
        return self.app.exec_()

if __name__ == "__main__":
    app = MainApp()
    sys.exit(app.run())
