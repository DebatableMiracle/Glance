from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QAction
from PyQt5.QtGui import QIcon

class SystemTray:
    def __init__(self, window):
        self.tray_icon = QSystemTrayIcon(QIcon("resources/icon.png"), window)

        menu = QMenu()
        show_action = QAction("Show", window)
        show_action.triggered.connect(window.show)
        quit_action = QAction("Quit", window)
        quit_action.triggered.connect(window.close)

        menu.addAction(show_action)
        menu.addAction(quit_action)
        self.tray_icon.setContextMenu(menu)
