# Glancing AI for Neuron-based Contextual Explanation (G.L.A.N.C.E.)

## Overview
Glance is a PyQt-based GUI application that enables users to utilize multimodal AI models across their entire PC. It captures real-time snapshots of the screen, processes them through user-specified API-based models, and provides context-aware explanations, answers, and assistance. The goal is to create an intuitive and persistent AI-powered assistant that enhances productivity and accessibility.

## Features
- **API-Based Visual Processing** – Supports various multimodal AI models, allowing users to integrate their own API keys.
- **Screen Context Analysis** – Takes screenshots to understand the current screen state and provide relevant insights.
- **User-Friendly PyQt GUI** – Designed for seamless interaction with a floating widget-based UI.
- **Cross-Platform Support** – Works on both Windows and Linux.
- **AI Assistant Capabilities** – Aims to function as an intelligent assistant by continuously improving contextual responses.
- **Work in Progress** – Actively evolving with planned support for local LLMs like LLaVA for offline processing.

## Installation
### Prerequisites
- Python 3.8+
- PyQt5
- API keys for AI models (e.g., Gemini, LLaVA, etc.)

### Setup
1. Clone the repository:
   ```sh
   git clone https://github.com/yourusername/Glance.git
   cd Glance
   ```
2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
3. Run the application:
   ```sh
   python main.py
   ```

## Usage
1. Launch G.L.A.N.C.E.
2. Configure API keys via the settings panel.
3. Click the floating widget to ask questions based on your screen’s content.
4. Receive AI-generated responses contextualized to your screen.

## Roadmap
- [ ] Implement local LLM support (e.g., LLaVA)
- [ ] Improve UI/UX for better user interaction
- [ ] Add more model integrations and API options
- [ ] Enhance performance and reduce latency

## Contributing
Contributions are welcome! Feel free to submit pull requests or open issues to help improve G.L.A.N.C.E.

## License
MIT License

---

G.L.A.N.C.E. is an ambitious project aimed at redefining AI-powered desktop assistance. Stay tuned for more updates!

