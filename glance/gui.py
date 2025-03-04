from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, QLabel, 
    QLineEdit, QStackedWidget, QFormLayout, QApplication, QSizeGrip, QSlider
)
from PyQt5.QtCore import Qt, QPoint, QSize

from qt_material import apply_stylesheet

from PyQt5.QtGui import QIcon
from glance.api import ApiWorker
from glance.screenshot import take_screenshot
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
        import os
        if os.environ.get('XDG_SESSION_TYPE') != 'wayland':
            self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Enable resizing
        self.setMinimumSize(300, 200)
        
        # Apply styling with custom background and muted colors
        apply_stylesheet(self, theme='dark_teal.xml')
        self.setStyleSheet(self.styleSheet() + """
            QWidget {
                background-color: rgba(33, 33, 33, 0.6);
            }
            QPushButton {
                background-color: rgba(38, 50, 56, 0.8);
                color: #adbdc1;
            }
            QPushButton:hover {
                background-color: rgba(55, 71, 79, 0.8);
            }
            QTextEdit, QLineEdit {
                background-color: rgba(38, 50, 56, 0.85);
                color: #adbdc1;
                border: 1px solid rgba(55, 71, 79, 0.85);
            }
            QLabel {
                color: #adbdc1;
            }
        """)
        


        # Initialize stacked widget for multiple pages
        self.stacked_widget = QStackedWidget()
        
        # Initialize UI components
        self.init_ui()
        
        # Create main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Add title bar and stacked widget
        main_layout.addWidget(self.title_bar)
        main_layout.addWidget(self.stacked_widget)
        
        self.setLayout(main_layout)

    def init_ui(self):
        # Create main page
        self.main_page = QWidget()
        main_layout = QVBoxLayout(self.main_page)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
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
        
        # Main content area
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)

        # Use QTextEdit instead of QLineEdit for multi-line input
        self.query_input = QTextEdit()
        self.query_input.setMinimumHeight(30)
        self.query_input.setMaximumHeight(100)  # Maximum 4 lines approximately
        self.query_input.setPlaceholderText("Ask something about your screen...")
        # Handle key events for submission
        self.query_input.installEventFilter(self)

        submit_button = QPushButton("Ask")
        submit_button.clicked.connect(self.process_query)

        input_layout = QHBoxLayout()
        input_layout.addWidget(self.query_input)
        input_layout.addWidget(submit_button)

        self.response_text = QTextEdit()
        self.response_text.setReadOnly(True)
        self.response_text.setPlaceholderText("Responses will appear here.")

        settings_button = QPushButton("Settings")
        settings_button.clicked.connect(self.show_settings_page)


        main_layout.addLayout(input_layout)
        main_layout.addWidget(self.response_text)
        main_layout.addWidget(settings_button)
        self.main_page.setLayout(main_layout)

        # Create settings page
        self.settings_page = QWidget()
        settings_layout = QVBoxLayout()

        settings_header = QHBoxLayout()
        settings_title = QLabel("Settings")
        settings_title.setStyleSheet("font-weight: bold; font-size: 14px;")
        back_button = QPushButton("Back")
        back_button.clicked.connect(self.show_main_page)
        settings_header.addWidget(settings_title)
        settings_header.addStretch()
        settings_header.addWidget(back_button)

        form_layout = QFormLayout()
        
        # Add model provider selection
        self.settings_model_provider = QLineEdit(self.model_provider)
        self.settings_model_provider.setPlaceholderText("openai or gemini")
        self.settings_model_provider.textChanged.connect(self.on_model_provider_changed)

        self.settings_api_endpoint = QLineEdit(self.api_endpoint)
        self.settings_api_endpoint.setPlaceholderText("Required for OpenAI, not used for Gemini")
        
        self.settings_api_key = QLineEdit(self.api_key)
        self.settings_api_key.setEchoMode(QLineEdit.Password)
        self.settings_api_key.setPlaceholderText("Your API key")

        form_layout.addRow("Model Provider:", self.settings_model_provider)
        form_layout.addRow("API Endpoint:", self.settings_api_endpoint)
        form_layout.addRow("API Key:", self.settings_api_key)
        


        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_settings)

        settings_layout.addLayout(settings_header)
        settings_layout.addLayout(form_layout)
        settings_layout.addWidget(save_button)
        settings_layout.addStretch()
        self.settings_page.setLayout(settings_layout)

        # Add pages to stacked widget
        self.stacked_widget.addWidget(self.main_page)
        self.stacked_widget.addWidget(self.settings_page)

    def eventFilter(self, obj, event):
        if obj == self.query_input and event.type() == event.KeyPress:
            if event.key() == Qt.Key_Return and event.modifiers() == Qt.ControlModifier:
                self.process_query()
                return True
        return super().eventFilter(obj, event)

    def process_query(self):
        query = self.query_input.toPlainText()
        if not query:
            self.response_text.setText("Please enter a question.")
            return

        if not self.api_key:
            self.response_text.setText("Please configure API settings first.")
            return

        # Store current opacity
        current_opacity = self.windowOpacity()
        
        # Make window fully transparent
        self.setWindowOpacity(0)
        
        # Process events to ensure window updates
        QApplication.processEvents()
        
        # Small delay to ensure window is hidden
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(100, lambda: self.take_screenshot_and_process(query, current_opacity))

    def take_screenshot_and_process(self, query, original_opacity):
        # Take screenshot while window is invisible
        screenshot_path = take_screenshot()
        
        # Restore window opacity
        self.setWindowOpacity(original_opacity)
        
        if not screenshot_path:
            self.response_text.setText("Failed to take screenshot.")
            return

        # Show loading state
        self.response_text.setText("Processing your request...")
        self.query_input.setEnabled(False)

        self.worker = ApiWorker(self.api_endpoint, self.api_key, screenshot_path, query, self.model_provider)
        self.worker.finished.connect(self.display_response)
        self.worker.error.connect(self.handle_error)
        self.worker.start()

    def display_response(self, response):
        self.query_input.setEnabled(True)
        if self.model_provider == 'gemini':
            # Gemini response is already formatted
            content = response.get("choices", [{}])[0].get("message", {}).get("content", "No response")
        else:
            # OpenAI response
            content = response.get("choices", [{}])[0].get("message", {}).get("content", "No response")
        self.response_text.setText(content)

    def handle_error(self, error_msg):
        self.query_input.setEnabled(True)
        self.response_text.setText(f"Error: {error_msg}")

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # Check if click is in title bar
            if self.title_bar.geometry().contains(event.pos()):
                import os
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

    def adjust_input_height(self):
        # Calculate required height based on content
        document = self.query_input.document()
        height = document.size().height() + 10  # Add padding
        # Limit maximum height
        height = min(height, 80)
        # Set new height
        self.query_input.setFixedHeight(int(height))

    def show_settings_page(self):
        self.stacked_widget.setCurrentWidget(self.settings_page)

    def show_main_page(self):
        self.stacked_widget.setCurrentWidget(self.main_page)

    def on_model_provider_changed(self, text):
        """Update UI based on selected model provider"""
        if text.lower() == 'gemini':
            self.settings_api_endpoint.setEnabled(False)
            self.settings_api_endpoint.setPlaceholderText("Not required for Gemini API")
        else:
            self.settings_api_endpoint.setEnabled(True)
            self.settings_api_endpoint.setPlaceholderText("Required for OpenAI API")

    def save_settings(self):
        # Validate model provider
        model_provider = self.settings_model_provider.text().lower()
        if model_provider not in ['openai', 'gemini']:
            self.response_text.setText("Error: Model provider must be either 'openai' or 'gemini'")
            return

        settings = {
            "api_endpoint": self.settings_api_endpoint.text(),
            "api_key": self.settings_api_key.text(),
            "model_provider": model_provider
        }
        
        self.api_endpoint = settings["api_endpoint"]
        self.api_key = settings["api_key"]
        self.model_provider = settings["model_provider"]
        
        save_settings(settings)
        self.show_main_page()
