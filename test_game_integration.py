#!/usr/bin/env python3
"""
Quick integration test for GameManager
"""

import tkinter as tk
from tkinter import ttk
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from games.game_manager import GameManager, GameType


def test_game_manager_integration():
    """Test GameManager integration"""
    print("Testing GameManager integration...")
    
    # Create root window
    root = tk.Tk()
    root.title("GameManager Integration Test")
    root.geometry("800x600")
    
    # Create main frame
    main_frame = ttk.Frame(root)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Create GameManager
    game_manager = GameManager(main_frame)
    
    # Set up status callback
    status_label = ttk.Label(root, text="Ready")
    status_label.pack(side=tk.BOTTOM, pady=5)
    
    def status_callback(message):
        status_label.config(text=message)
        print(f"Status: {message}")
    
    game_manager.set_status_callback(status_callback)
    
    # Test buttons
    button_frame = ttk.Frame(root)
    button_frame.pack(side=tk.BOTTOM, pady=5)
    
    ttk.Button(
        button_frame,
        text="Test Tic-Tac-Toe",
        command=lambda: game_manager.start_game(GameType.TIC_TAC_TOE)
    ).pack(side=tk.LEFT, padx=5)
    
    ttk.Button(
        button_frame,
        text="Test Connect 4",
        command=lambda: game_manager.start_game(GameType.CONNECT_4)
    ).pack(side=tk.LEFT, padx=5)
    
    ttk.Button(
        button_frame,
        text="Test Battleship",
        command=lambda: game_manager.start_game(GameType.BATTLESHIP)
    ).pack(side=tk.LEFT, padx=5)
    
    ttk.Button(
        button_frame,
        text="Back to Selection",
        command=game_manager.show_game_selection
    ).pack(side=tk.LEFT, padx=5)
    
    ttk.Button(
        button_frame,
        text="Exit",
        command=root.quit
    ).pack(side=tk.LEFT, padx=5)
    
    print("GameManager integration test window opened.")
    print("Use the buttons to test game selection and switching.")
    print("Close the window when done testing.")
    
    # Run the test
    root.mainloop()
    
    print("GameManager integration test completed.")


if __name__ == "__main__":
    test_game_manager_integration()