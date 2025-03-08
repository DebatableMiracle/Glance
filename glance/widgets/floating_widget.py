# widgets/floating_widget.py
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QStackedWidget
)
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QIcon
from qt_material import apply_stylesheet
import os

from pages.home_page import MainPage
from pages.settings_page import SettingsPage
from glance.settings import load_settings, save_settings

class FloatingWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.config = load_settings()
        self.api_endpoint = self.config.get("api_endpoint", "")
        self.api_key = self.config.get("api_key", "")
        self.model_provider = self.config.get("model_provider", "openai")
        
        # Set window opacity
        self.setWindowOpacity(0.95)

        # For window dragging
        self.dragging = False
        self.offset = QPoint()

        self.setWindowTitle("GLANCE")
        # Use standard window flags for better Wayland compatibility
        self.setWindowFlags(Qt.Window | Qt.WindowStaysOnTopHint | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint)
        # Don't use translucent background on Wayland
        if os.environ.get('XDG_SESSION_TYPE') != 'wayland':
            self.setAttribute(Qt.WA_TranslucentBackground)
        # Enable resizing
        self.setMinimumSize(300, 200)
        
        # Apply styling with custom background and muted colors
        apply_stylesheet(self, theme='dark_blue.xml')
        self.setStyleSheet(self.styleSheet() + """
    QWidget {
        background-color: rgba(15, 20, 30, 0.6);
    }
    QPushButton {
        background-color: rgba(20, 30, 45, 0.8);
        color: #a1c4e3;
    }   
    QPushButton:hover {
        background-color: rgba(30, 40, 55, 0.8);
    }
    QTextEdit, QLineEdit {
        background-color: rgba(20, 30, 45, 0.85);
        color: #a1c4e3;
        border: 1px solid rgba(35, 45, 60, 0.85);
    }
    QLabel {
        color: #a1c4e3;
    }
""")
        # Initialize stacked widget for multiple pages
        self.stacked_widget = QStackedWidget()
        
        # Create title bar
        self.create_title_bar()
        
        # Initialize pages
        self.init_pages()
        
        # Create main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Add title bar and stacked widget
        main_layout.addWidget(self.title_bar)
        main_layout.addWidget(self.stacked_widget)
        
        self.setLayout(main_layout)

    def create_title_bar(self):
        # Create title bar
        title_bar = QWidget()
        title_bar.setFixedHeight(30)
        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(10, 0, 10, 0)
        
        title_label = QLabel("GLANCE")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        
        # Store title bar for dragging
        self.title_bar = title_bar

    def init_pages(self):
        # Create main page
        self.main_page = MainPage(self)
        
        # Create settings page
        self.settings_page = SettingsPage(self)
        
        # Add pages to stacked widget
        self.stacked_widget.addWidget(self.main_page)
        self.stacked_widget.addWidget(self.settings_page)
        
        # Set initial page
        self.show_main_page()

    def show_settings_page(self):
        self.settings_page.update_fields(self.api_endpoint, self.api_key, self.model_provider)
        self.stacked_widget.setCurrentWidget(self.settings_page)

    def show_main_page(self):
        self.stacked_widget.setCurrentWidget(self.main_page)

    def save_settings(self, api_endpoint, api_key, model_provider):
        settings = {
            "api_endpoint": api_endpoint,
            "api_key": api_key,
            "model_provider": model_provider
        }
        
        self.api_endpoint = settings["api_endpoint"]
        self.api_key = settings["api_key"]
        self.model_provider = settings["model_provider"]
        
        save_settings(settings)
        self.show_main_page()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # Check if click is in title bar
            if self.title_bar.geometry().contains(event.pos()):
                if os.environ.get('XDG_SESSION_TYPE') != 'wayland':
                    self.dragging = True
                    self.offset = event.pos()
                else:
                    # Let Wayland handle window dragging
                    self.windowHandle().startSystemMove()

    def mouseMoveEvent(self, event):
        if hasattr(self, 'dragging') and self.dragging and event.buttons() & Qt.LeftButton:
            self.move(event.globalPos() - self.offset)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and hasattr(self, 'dragging'):
            self.dragging = False