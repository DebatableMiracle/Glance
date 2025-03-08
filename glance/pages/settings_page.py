# pages/settings_page.py
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QFormLayout
)

class SettingsPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.init_ui()

    def init_ui(self):
        settings_layout = QVBoxLayout(self)
        settings_layout.setContentsMargins(10, 10, 10, 10)

        settings_header = QHBoxLayout()
        settings_title = QLabel("Settings")
        settings_title.setStyleSheet("font-weight: bold; font-size: 14px;")
        back_button = QPushButton("Back")
        back_button.clicked.connect(self.parent.show_main_page)
        settings_header.addWidget(settings_title)
        settings_header.addStretch()
        settings_header.addWidget(back_button)

        form_layout = QFormLayout()
        
        # Add model provider selection
        self.settings_model_provider = QLineEdit()
        self.settings_model_provider.setPlaceholderText("openai or gemini")
        self.settings_model_provider.textChanged.connect(self.on_model_provider_changed)

        self.settings_api_endpoint = QLineEdit()
        self.settings_api_endpoint.setPlaceholderText("Required for OpenAI, not used for Gemini")
        
        self.settings_api_key = QLineEdit()
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

    def update_fields(self, api_endpoint, api_key, model_provider):
        """Update field values when page is shown"""
        self.settings_api_endpoint.setText(api_endpoint)
        self.settings_api_key.setText(api_key)
        self.settings_model_provider.setText(model_provider)
        # Update UI based on model provider
        self.on_model_provider_changed(model_provider)

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
            self.parent.main_page.response_text.setText("Error: Model provider must be either 'openai' or 'gemini'")
            self.parent.show_main_page()
            return

        # Call parent's save_settings method with new values
        self.parent.save_settings(
            self.settings_api_endpoint.text(),
            self.settings_api_key.text(),
            model_provider
        )