# pages/main_page.py
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton
)
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication

from glance.api import ApiWorker
from glance.screenshot import take_screenshot

class MainPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)

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
        settings_button.clicked.connect(self.parent.show_settings_page)

        main_layout.addLayout(input_layout)
        main_layout.addWidget(self.response_text)
        main_layout.addWidget(settings_button)

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

        if not self.parent.api_key:
            self.response_text.setText("Please configure API settings first.")
            return

        # Store current opacity
        current_opacity = self.parent.windowOpacity()
        
        # Make window fully transparent
        self.parent.setWindowOpacity(0)
        
        # Process events to ensure window updates
        QApplication.processEvents()
        
        # Small delay to ensure window is hidden
        QTimer.singleShot(100, lambda: self.take_screenshot_and_process(query, current_opacity))

    def take_screenshot_and_process(self, query, original_opacity):
        # Take screenshot while window is invisible
        screenshot_path = take_screenshot()
        
        # Restore window opacity
        self.parent.setWindowOpacity(original_opacity)
        
        if not screenshot_path:
            self.response_text.setText("Failed to take screenshot.")
            return

        # Show loading state
        self.response_text.setText("Processing your request...")
        self.query_input.setEnabled(False)

        self.worker = ApiWorker(
            self.parent.api_endpoint, 
            self.parent.api_key, 
            screenshot_path, 
            query, 
            self.parent.model_provider
        )
        self.worker.finished.connect(self.display_response)
        self.worker.error.connect(self.handle_error)
        self.worker.start()

    def display_response(self, response):
        self.query_input.setEnabled(True)
        if self.parent.model_provider == 'gemini':
            # Gemini response is already formatted
            content = response.get("choices", [{}])[0].get("message", {}).get("content", "No response")
        else:
            # OpenAI response
            content = response.get("choices", [{}])[0].get("message", {}).get("content", "No response")
        self.response_text.setText(content)

    def handle_error(self, error_msg):
        self.query_input.setEnabled(True)
        self.response_text.setText(f"Error: {error_msg}")

    def adjust_input_height(self):
        # Calculate required height based on content
        document = self.query_input.document()
        height = document.size().height() + 10  # Add padding
        # Limit maximum height
        height = min(height, 80)
        # Set new height
        self.query_input.setFixedHeight(int(height))