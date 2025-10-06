"""
Tic-Tac-Toe Game Implementation for Z.E.U.S. Virtual Assistant
Features a 3x3 grid with intelligent AI opponent using minimax algorithm
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Tuple, Optional, Union
from dataclasses import dataclass
import copy


@dataclass
class TicTacToeState:
    """Represents the state of a Tic-Tac-Toe game"""
    board: List[List[str]]
    current_player: str
    winner: Optional[str]
    game_over: bool
    move_count: int


class TicTacToeGame:
    """Tic-Tac-Toe game with AI opponent using minimax algorithm"""
    
    def __init__(self, parent_frame: ttk.Frame, status_callback=None, back_callback=None, end_game_callback=None):
        self.parent_frame = parent_frame
        self.status_callback = status_callback
        self.back_callback = back_callback
        self.end_game_callback = end_game_callback
        
        # Game state
        self.board = [['', '', ''] for _ in range(3)]
        self.current_player = 'X'  # Human is X, AI is O
        self.game_over = False
        self.winner = None
        self.move_count = 0
        
        # UI elements
        self.buttons = []
        self.game_frame = None
        self.info_frame = None
        self.current_player_label = None
        
        # Initialize the game UI
        self.setup_game_ui()
        self.update_status("Your turn! Click any square to make your move.")
    
    def setup_game_ui(self):
        """Create the Tic-Tac-Toe game interface"""
        # Clear any existing content
        for widget in self.parent_frame.winfo_children():
            widget.destroy()
        
        # Main container
        main_container = ttk.Frame(self.parent_frame)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Header section
        header_frame = ttk.Frame(main_container)
        header_frame.pack(fill=tk.X, pady=(20, 10))
        
        # Title
        title_label = ttk.Label(
            header_frame,
            text="⭕ Tic-Tac-Toe",
            font=("Arial", 24, "bold"),
            foreground="#0078d4"
        )
        title_label.pack()
        
        # Game info section
        self.info_frame = ttk.Frame(main_container)
        self.info_frame.pack(pady=10)
        
        # Current player indicator
        self.current_player_label = ttk.Label(
            self.info_frame,
            text="Your Turn (X)",
            font=("Arial", 14, "bold"),
            foreground="#0078d4"
        )
        self.current_player_label.pack()
        
        # Game board section
        self.game_frame = ttk.Frame(main_container)
        self.game_frame.pack(expand=True, pady=20)
        
        # Create 3x3 grid of buttons
        self.buttons = []
        for row in range(3):
            button_row = []
            for col in range(3):
                button = tk.Button(
                    self.game_frame,
                    text='',
                    font=("Arial", 24, "bold"),
                    width=4,
                    height=2,
                    command=lambda r=row, c=col: self.make_move(r, c),
                    bg="#f0f0f0",
                    relief=tk.RAISED,
                    borderwidth=2
                )
                button.grid(row=row, column=col, padx=2, pady=2)
                button_row.append(button)
            self.buttons.append(button_row)
        
        # Control buttons section
        controls_frame = ttk.Frame(main_container)
        controls_frame.pack(side=tk.BOTTOM, pady=20)
        
        # New game button
        new_game_button = ttk.Button(
            controls_frame,
            text="🔄 New Game",
            command=self.reset_game
        )
        new_game_button.pack(side=tk.LEFT, padx=10)
        
        # Back to selection button
        back_button = ttk.Button(
            controls_frame,
            text="← Back to Games",
            command=self.back_to_selection
        )
        back_button.pack(side=tk.LEFT, padx=10)
    
    def make_move(self, row: int, col: int) -> bool:
        """Make a move at the specified position"""
        # Check if move is valid
        if self.game_over or self.board[row][col] != '' or self.current_player != 'X':
            return False
        
        # Make the move
        self.board[row][col] = 'X'
        self.buttons[row][col].config(text='X', fg='#0078d4', state='disabled')
        self.move_count += 1
        
        # Check for win or draw
        if self.check_winner():
            self.end_game(self.check_winner())
            return True
        
        if self.is_board_full():
            self.end_game(None)  # Draw
            return True
        
        # Switch to AI turn
        self.current_player = 'O'
        self.update_player_display()
        self.update_status("AI is thinking...")
        
        # Schedule AI move after a short delay for better UX
        self.parent_frame.after(500, self.make_ai_move)
        
        return True
    
    def make_ai_move(self):
        """Make AI move using minimax algorithm"""
        if self.game_over:
            return
        
        # Get best move from minimax algorithm
        row, col = self.get_ai_move()
        
        if row is not None and col is not None:
            # Make the AI move
            self.board[row][col] = 'O'
            self.buttons[row][col].config(text='O', fg='#d13438', state='disabled')
            self.move_count += 1
            
            # Check for win or draw
            if self.check_winner():
                self.end_game(self.check_winner())
                return
            
            if self.is_board_full():
                self.end_game(None)  # Draw
                return
            
            # Switch back to human turn
            self.current_player = 'X'
            self.update_player_display()
            self.update_status("Your turn! Click any square to make your move.")
    
    def get_ai_move(self) -> Tuple[Optional[int], Optional[int]]:
        """Get the best move for AI using minimax algorithm"""
        best_score = float('-inf')
        best_move = (None, None)
        
        for row in range(3):
            for col in range(3):
                if self.board[row][col] == '':
                    # Try this move
                    self.board[row][col] = 'O'
                    score = self.minimax(self.board, 0, False)
                    self.board[row][col] = ''  # Undo move
                    
                    if score > best_score:
                        best_score = score
                        best_move = (row, col)
        
        return best_move
    
    def minimax(self, board: List[List[str]], depth: int, is_maximizing: bool) -> int:
        """Minimax algorithm for optimal AI moves"""
        winner = self.check_winner_on_board(board)
        
        # Terminal states
        if winner == 'O':  # AI wins
            return 10 - depth
        elif winner == 'X':  # Human wins
            return depth - 10
        elif self.is_board_full_check(board):  # Draw
            return 0
        
        if is_maximizing:
            # AI's turn - maximize score
            best_score = float('-inf')
            for row in range(3):
                for col in range(3):
                    if board[row][col] == '':
                        board[row][col] = 'O'
                        score = self.minimax(board, depth + 1, False)
                        board[row][col] = ''
                        best_score = max(score, best_score)
            return best_score
        else:
            # Human's turn - minimize score
            best_score = float('inf')
            for row in range(3):
                for col in range(3):
                    if board[row][col] == '':
                        board[row][col] = 'X'
                        score = self.minimax(board, depth + 1, True)
                        board[row][col] = ''
                        best_score = min(score, best_score)
            return best_score
    
    def check_winner(self) -> Optional[str]:
        """Check if there's a winner on the current board"""
        return self.check_winner_on_board(self.board)
    
    def check_winner_on_board(self, board: List[List[str]]) -> Optional[str]:
        """Check if there's a winner on the given board"""
        # Check rows
        for row in board:
            if row[0] == row[1] == row[2] != '':
                return row[0]
        
        # Check columns
        for col in range(3):
            if board[0][col] == board[1][col] == board[2][col] != '':
                return board[0][col]
        
        # Check diagonals
        if board[0][0] == board[1][1] == board[2][2] != '':
            return board[0][0]
        
        if board[0][2] == board[1][1] == board[2][0] != '':
            return board[0][2]
        
        return None
    
    def is_board_full(self) -> bool:
        """Check if the current board is full"""
        return self.is_board_full_check(self.board)
    
    def is_board_full_check(self, board: List[List[str]]) -> bool:
        """Check if the given board is full"""
        for row in board:
            for cell in row:
                if cell == '':
                    return False
        return True
    
    def end_game(self, winner: Optional[str]):
        """End the game and show result"""
        self.game_over = True
        self.winner = winner
        
        # Disable all buttons
        for row in self.buttons:
            for button in row:
                button.config(state='disabled')
        
        # Show result
        if winner == 'X':
            result_text = "🎉 Congratulations! You won!"
            self.update_status("You won! Great job!")
        elif winner == 'O':
            result_text = "🤖 AI wins! Better luck next time!"
            self.update_status("AI won this round. Try again!")
        else:
            result_text = "🤝 It's a draw! Good game!"
            self.update_status("It's a draw! Well played!")
        
        # Update player display to show result
        self.current_player_label.config(
            text=result_text,
            foreground="#0078d4" if winner == 'X' else "#d13438" if winner == 'O' else "#666666"
        )
        
        # Notify game manager of game end
        if self.end_game_callback:
            winner_name = "player" if winner == 'X' else "ai" if winner == 'O' else None
            self.end_game_callback(winner_name)
        else:
            # Show popup with result if no callback
            messagebox.showinfo("Game Over", result_text)
    
    def reset_game(self):
        """Reset the game to initial state"""
        # Reset game state
        self.board = [['', '', ''] for _ in range(3)]
        self.current_player = 'X'
        self.game_over = False
        self.winner = None
        self.move_count = 0
        
        # Reset UI
        for row in self.buttons:
            for button in row:
                button.config(text='', state='normal', bg="#f0f0f0")
        
        self.update_player_display()
        self.update_status("New game started! Your turn.")
    
    def update_player_display(self):
        """Update the current player display"""
        if self.current_player == 'X':
            self.current_player_label.config(
                text="Your Turn (X)",
                foreground="#0078d4"
            )
        else:
            self.current_player_label.config(
                text="AI Turn (O)",
                foreground="#d13438"
            )
    
    def update_status(self, message: str):
        """Update status message"""
        if self.status_callback:
            self.status_callback(message)
    
    def back_to_selection(self):
        """Return to game selection"""
        if self.back_callback:
            self.back_callback()
    
    def get_game_state(self) -> TicTacToeState:
        """Get current game state"""
        return TicTacToeState(
            board=copy.deepcopy(self.board),
            current_player=self.current_player,
            winner=self.winner,
            game_over=self.game_over,
            move_count=self.move_count
        )