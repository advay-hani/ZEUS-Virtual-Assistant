# Z.E.U.S. Virtual Assistant

Zero-cost Enhanced User Support - A lightweight AI-powered virtual assistant for PC.

## Project Structure

```
zeus-virtual-assistant/
├── main.py              # Main application entry point
├── requirements.txt     # Python dependencies
├── README.md           # Project documentation
├── models/             # Data models
│   └── __init__.py
├── ui/                 # User interface components
│   └── __init__.py
├── games/              # Game implementations
│   └── __init__.py
└── core/               # Core modules (AI engine, document processor)
    └── __init__.py
```

## Installation

1. Install Python 3.8 or higher
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

### Development Mode
```bash
python main.py
```

### Building Distribution Package
```bash
# Validate build environment
python validate_package.py

# Build standalone executable
python build_package.py
```

The build process creates a standalone executable in `dist/Zeus-Virtual-Assistant.zip` that can be distributed to end users.

## Features

- Offline AI chat assistant
- Document analysis (PDF, DOC, DOCX)
- Interactive games (Tic-Tac-Toe, Connect 4, Battleship)
- Resource-efficient operation (< 1GB)