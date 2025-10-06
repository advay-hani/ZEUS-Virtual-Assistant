#!/usr/bin/env python3
"""
Z.E.U.S. (Zero-cost Enhanced User Support) Virtual Assistant
Main application entry point
"""

import sys
import os

# Add the project root to Python path 
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.main_window import ZeusMainWindow


def main():
    """Main entry point for the application"""
    try:
        app = ZeusMainWindow()
        app.run()
    except Exception as e:
        print(f"Error starting Z.E.U.S. Virtual Assistant: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()