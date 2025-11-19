# GemGuard AI 🛡️

<p align="center">
  <img src="img/gem_guard.png" alt="GemGuard AI Interface" width="800"/>
</p>

**GemGuard AI** is a powerful terminal-based security analysis tool that brings AI-powered system auditing to Linux environments. Built specifically for Fedora and RPM-based distributions, it combines Google's advanced Gemini AI models with real-time system monitoring to deliver actionable security insights directly in your terminal.

## ✨ Why GemGuard AI?

Traditional security tools often require deep technical expertise to interpret. GemGuard AI bridges this gap by using artificial intelligence to analyze system data and explain potential threats in plain language, making enterprise-grade security accessible to everyone.

## 🚀 Key Features

- **🤖 AI-Powered Intelligence**: Leverages Gemini 1.5 Flash, Pro, and 2.0 models to transform raw system logs into clear, actionable security recommendations
- **🖥️ Smart Process Monitoring**: Analyzes CPU-intensive processes, detecting obfuscated names, privilege escalations, and suspicious behaviors
- **🌐 Network Security Auditing**: Examines active connections using `ss` to identify unauthorized ports, suspicious remote IPs, and potential data exfiltration
- **📦 Package Integrity Checks**: Reviews recently installed RPM and Flatpak packages to detect unauthorized software, bloatware, and malicious installations
- **🌍 Multilingual Interface**: Complete support for English (EN-US) and Portuguese (PT-BR), including localized reports and diagnostics
- **🎨 Modern Terminal UI**: Beautiful interface powered by Textual, featuring dark mode, smooth animations, and intuitive mouse support
- **⚡ Flexible Model Selection**: Switch between Gemini models on the fly—use Flash for quick scans or Pro for in-depth analysis
- **📊 Comprehensive Reporting**: Generate full system security reports that cross-reference processes, network activity, and package installations

<p align="center">
  <img src="img/package_result.png" alt="Package Analysis Results" width="800"/>
</p>

## 🛠️ Prerequisites

| Requirement | Details |
|------------|---------|
| **Operating System** | Linux (optimized for Fedora Workstation and RPM-based distributions) |
| **Python Version** | 3.10 or higher |
| **API Access** | Valid Google AI Studio API key ([Get one here](https://makersuite.google.com/app/apikey)) |
| **Dependencies** | `textual`, `google-genai`, `python-dotenv` |

## 📥 Installation

### Quick Start

```bash
# Clone the repository
git clone https://github.com/your-username/gem-guard.git
cd gem-guard

# Create and activate virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Linux/Mac
# On Windows: venv\Scripts\activate

# Install dependencies
pip install textual google-genai python-dotenv
```

### Alternative: Using `requirements.txt`

```bash
pip install -r requirements.txt
```

## ⚙️ Configuration

1. **Create environment file:**
   ```bash
   touch .env
   ```

2. **Add your API key:**
   ```env
   GEMINI_API_KEY=your_actual_api_key_here
   ```

3. **Verify permissions** (ensure you can execute system commands):
   ```bash
   chmod +x main.py
   ```

## 🚀 Usage

### Starting the Application

```bash
python main.py
```

### Interface Guide

| Element | Function |
|---------|----------|
| **Language Selector** | Choose between 🇧🇷 PT-BR and 🇺🇸 EN-US |
| **Model Dropdown** | Select AI model (Flash/Pro/2.0) based on speed vs. depth needs |
| **Processes/Processos** | Audit running tasks and identify suspicious processes |
| **Network/Rede** | Analyze network connections and detect unauthorized access |
| **Packages/Pacotes** | Review recent software installations |
| **Full/Relatório** | Generate comprehensive security report |

### Keyboard Shortcuts

- `d` - Toggle Dark/Light mode
- `q` - Quit application
- `p` - Open command palette

## 🏗️ Project Architecture

```
gem-guard/
├── main.py           # TUI implementation, widgets, and event handling (Textual)
├── system.py         # Backend logic, shell commands, AI prompt engineering
├── .env              # Environment variables (API keys) - NOT in version control
├── .env.example      # Template for environment configuration
├── requirements.txt  # Python dependencies
├── img/
│   ├── gem_guard.png        # Main interface screenshot
│   └── package_result.png   # Analysis results example
└── README.md         # This file
```

### Core Components

- **`main.py`**: Manages the Textual-based user interface, handles user interactions, and coordinates between UI elements and backend services
- **`system.py`**: Executes Linux commands (`ps`, `ss`, `rpm`, `dnf`), constructs AI prompts, and interfaces with Google's GenAI SDK for analysis

## ⚠️ Important Disclaimers

**GemGuard AI is an assistive tool, not a replacement for professional security audits.**

- 🧠 **AI Limitations**: Large language models can occasionally produce false positives or "hallucinations." Always verify critical alerts manually
- 🔍 **Manual Verification**: Cross-reference findings with standard Linux tools: `top`, `htop`, `netstat`, `wireshark`, `auditd`
- 📋 **Use Case**: Ideal for initial security assessments, educational purposes, and routine monitoring—not for mission-critical production environments without validation
- ⚖️ **Liability**: The developers assume no responsibility for actions taken based solely on AI-generated recommendations

## 🤝 Contributing

We welcome contributions from the community! Whether it's bug fixes, new features, or documentation improvements, your help makes GemGuard AI better for everyone.

### How to Contribute

1. **Fork** the repository
2. **Create** a feature branch
   ```bash
   git checkout -b feature/AmazingSecurityFeature
   ```
3. **Commit** your changes with clear messages
   ```bash
   git commit -m 'Add advanced port scanning detection'
   ```
4. **Push** to your branch
   ```bash
   git push origin feature/AmazingSecurityFeature
   ```
5. **Open** a Pull Request with a detailed description

### Contribution Ideas

- 🐧 Support for additional Linux distributions (Debian, Arch, etc.)
- 🔌 Integration with other system monitoring tools
- 📊 Enhanced visualization and reporting features
- 🌐 Additional language translations
- 🧪 Unit tests and integration tests

## 📄 License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for complete details
