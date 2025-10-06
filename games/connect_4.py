"""
Connect 4 Game Implementation for Z.E.U.S. Virtual Assistant
Features a 6x7 grid with piece dropping mechanics and intelligent AI opponent using minimax with alpha-beta pruning
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Tuple, Optional, Union
from dataclasses import dataclass
import copy


@dataclass
class Connect4State:
    """Represents the state of a Connect 4 game"""
    board: List[List[str]]
    current_player: str
    winner: Optional[str]
    game_over: bool
    move_count: int
    last_move: Optional[Tuple[int, int]]


class Connect4Game:
    """Connect 4 game with AI opponent using minimax with alpha-beta pruning"""
    
    def __init__(self, parent_frame: ttk.Frame, status_callback=None, back_callback=None, end_game_callback=None):
        self.parent_frame = parent_frame
        self.status_callback = status_callback
        self.back_callback = back_callback
        self.end_game_callback = end_game_callback
        
        # Game constants
        self.ROWS = 6
        self.COLS = 7
        self.CONNECT_COUNT = 4
        
        # Game state
        self.board = [['' for _ in range(self.COLS)] for _ in range(self.ROWS)]
        self.current_player = 'R'  # Human is Red (R), AI is Yellow (Y)
        self.game_over = False
        self.winner = None
        self.move_count = 0
        self.last_move = None
        
        # UI elements
        self.buttons = []
        self.board_buttons = []
        self.game_frame = None
        self.info_frame = None
        self.current_player_label = None
        
        # Initialize the game UI
        self.setup_game_ui()
        self.update_status("Your turn! Click any column to drop your red piece.")
    
    def setup_game_ui(self):
        """Create the Connect 4 game interface"""
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
            text="🔴 Connect 4",
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
            text="Your Turn (Red)",
            font=("Arial", 14, "bold"),
            foreground="#d13438"
        )
        self.current_player_label.pack()
        
        # Instructions
        instructions_label = ttk.Label(
            self.info_frame,
            text="Connect 4 pieces vertically, horizontally, or diagonally to win!",
            font=("Arial", 10),
            foreground="#666666"
        )
        instructions_label.pack(pady=(5, 0))
        
        # Game board section
        board_container = ttk.Frame(main_container)
        board_container.pack(expand=True, pady=20)
        
        # Column selection buttons (for dropping pieces)
        self.buttons = []
        button_frame = ttk.Frame(board_container)
        button_frame.pack(pady=(0, 10))
        
        for col in range(self.COLS):
            button = tk.Button(
                button_frame,
                text=f"↓",
                font=("Arial", 16, "bold"),
                width=3,
                height=1,
                command=lambda c=col: self.drop_piece(c),
                bg="#e0e0e0",
                relief=tk.RAISED,
                borderwidth=2
            )
            button.pack(side=tk.LEFT, padx=2)
            self.buttons.append(button)
        
        # Game board display
        self.game_frame = ttk.Frame(board_container)
        self.game_frame.pack()
        
        # Create 6x7 grid of display buttons (non-interactive)
        self.board_buttons = []
        for row in range(self.ROWS):
            button_row = []
            for col in range(self.COLS):
                button = tk.Button(
                    self.game_frame,
                    text='',
                    font=("Arial", 20, "bold"),
                    width=3,
                    height=1,
                    bg="#f0f0f0",
                    relief=tk.SUNKEN,
                    borderwidth=2,
                    state='disabled'
                )
                button.grid(row=row, column=col, padx=1, pady=1)
                button_row.append(button)
            self.board_buttons.append(button_row)
        
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
    
    def drop_piece(self, column: int) -> bool:
        """Drop a piece in the specified column"""
        # Check if move is valid
        if self.game_over or self.current_player != 'R' or not self.is_valid_column(column):
            return False
        
        # Find the lowest available row in the column
        row = self.get_next_open_row(column)
        if row is None:
            return False
        
        # Make the move
        self.board[row][column] = 'R'
        self.board_buttons[row][column].config(text='●', fg='#d13438', bg='#ffcccc')
        self.move_count += 1
        self.last_move = (row, column)
        
        # Animate the piece drop (simple visual feedback)
        self.animate_piece_drop(column, row)
        
        # Check for win or draw
        if self.check_winner():
            self.end_game(self.check_winner())
            return True
        
        if self.is_board_full():
            self.end_game(None)  # Draw
            return True
        
        # Switch to AI turn
        self.current_player = 'Y'
        self.update_player_display()
        self.update_status("AI is thinking...")
        
        # Disable column buttons during AI turn
        for button in self.buttons:
            button.config(state='disabled')
        
        # Schedule AI move after a short delay for better UX
        self.parent_frame.after(800, self.make_ai_move)
        
        return True
    
    def animate_piece_drop(self, column: int, final_row: int):
        """Simple animation effect for piece dropping"""
        # This is a simple visual feedback - could be enhanced with actual animation
        for row in range(final_row + 1):
            if row < final_row:
                # Temporarily highlight the path
                self.board_buttons[row][column].config(bg='#ffe0e0')
                self.parent_frame.update()
                self.parent_frame.after(50)
                self.board_buttons[row][column].config(bg='#f0f0f0')
    
    def make_ai_move(self):
        """Make AI move using minimax with alpha-beta pruning"""
        if self.game_over:
            return
        
        # Get best move from minimax algorithm
        column = self.get_ai_move()
        
        if column is not None and self.is_valid_column(column):
            # Find the row for this column
            row = self.get_next_open_row(column)
            
            if row is not None:
                # Make the AI move
                self.board[row][column] = 'Y'
                self.board_buttons[row][column].config(text='●', fg='#ffa500', bg='#fff5cc')
                self.move_count += 1
                self.last_move = (row, column)
                
                # Animate AI piece drop
                self.animate_ai_piece_drop(column, row)
                
                # Check for win or draw
                if self.check_winner():
                    self.end_game(self.check_winner())
                    return
                
                if self.is_board_full():
                    self.end_game(None)  # Draw
                    return
                
                # Switch back to human turn
                self.current_player = 'R'
                self.update_player_display()
                self.update_status("Your turn! Click any column to drop your red piece.")
                
                # Re-enable column buttons
                for col, button in enumerate(self.buttons):
                    if self.is_valid_column(col):
                        button.config(state='normal')
                    else:
                        button.config(state='disabled')
    
    def animate_ai_piece_drop(self, column: int, final_row: int):
        """Simple animation effect for AI piece dropping"""
        for row in range(final_row + 1):
            if row < final_row:
                # Temporarily highlight the path
                self.board_buttons[row][column].config(bg='#fff0cc')
                self.parent_frame.update()
                self.parent_frame.after(50)
                self.board_buttons[row][column].config(bg='#f0f0f0')
    
    def is_valid_column(self, column: int) -> bool:
        """Check if a column is valid for dropping a piece"""
        if column < 0 or column >= self.COLS:
            return False
        return self.board[0][column] == ''
    
    def get_next_open_row(self, column: int) -> Optional[int]:
        """Get the next available row in a column (gravity simulation)"""
        for row in range(self.ROWS - 1, -1, -1):
            if self.board[row][column] == '':
                return row
        return None
    
    def get_ai_move(self) -> Optional[int]:
        """Get the best move for AI using minimax with alpha-beta pruning"""
        _, best_column = self.minimax(self.board, 5, float('-inf'), float('inf'), True)
        return best_column
    
    def minimax(self, board: List[List[str]], depth: int, alpha: float, beta: float, maximizing_player: bool) -> Tuple[int, Optional[int]]:
        """Minimax algorithm with alpha-beta pruning for optimal AI moves"""
        valid_columns = [col for col in range(self.COLS) if self.is_valid_column_on_board(board, col)]
        
        # Check terminal states
        winner = self.check_winner_on_board(board)
        if winner == 'Y':  # AI wins
            return 100000, None
        elif winner == 'R':  # Human wins
            return -100000, None
        elif len(valid_columns) == 0:  # Draw
            return 0, None
        elif depth == 0:
            return self.evaluate_board(board), None
        
        if maximizing_player:
            # AI's turn - maximize score
            max_eval = float('-inf')
            best_column = valid_columns[0] if valid_columns else None
            
            for col in valid_columns:
                # Make a copy of the board and simulate the move
                board_copy = [row[:] for row in board]
                row = self.get_next_open_row_on_board(board_copy, col)
                if row is not None:
                    board_copy[row][col] = 'Y'
                    
                    eval_score, _ = self.minimax(board_copy, depth - 1, alpha, beta, False)
                    
                    if eval_score > max_eval:
                        max_eval = eval_score
                        best_column = col
                    
                    alpha = max(alpha, eval_score)
                    if beta <= alpha:
                        break  # Alpha-beta pruning
            
            return max_eval, best_column
        else:
            # Human's turn - minimize score
            min_eval = float('inf')
            best_column = valid_columns[0] if valid_columns else None
            
            for col in valid_columns:
                # Make a copy of the board and simulate the move
                board_copy = [row[:] for row in board]
                row = self.get_next_open_row_on_board(board_copy, col)
                if row is not None:
                    board_copy[row][col] = 'R'
                    
                    eval_score, _ = self.minimax(board_copy, depth - 1, alpha, beta, True)
                    
                    if eval_score < min_eval:
                        min_eval = eval_score
                        best_column = col
                    
                    beta = min(beta, eval_score)
                    if beta <= alpha:
                        break  # Alpha-beta pruning
            
            return min_eval, best_column
    
    def evaluate_board(self, board: List[List[str]]) -> int:
        """Evaluate the board position for the AI"""
        score = 0
        
        # Score center column preference
        center_col = self.COLS // 2
        center_count = sum(1 for row in range(self.ROWS) if board[row][center_col] == 'Y')
        score += center_count * 3
        
        # Evaluate all possible 4-piece windows
        # Horizontal
        for row in range(self.ROWS):
            for col in range(self.COLS - 3):
                window = [board[row][col + i] for i in range(4)]
                score += self.evaluate_window(window)
        
        # Vertical
        for col in range(self.COLS):
            for row in range(self.ROWS - 3):
                window = [board[row + i][col] for i in range(4)]
                score += self.evaluate_window(window)
        
        # Positive diagonal
        for row in range(self.ROWS - 3):
            for col in range(self.COLS - 3):
                window = [board[row + i][col + i] for i in range(4)]
                score += self.evaluate_window(window)
        
        # Negative diagonal
        for row in range(self.ROWS - 3):
            for col in range(3, self.COLS):
                window = [board[row + i][col - i] for i in range(4)]
                score += self.evaluate_window(window)
        
        return score
    
    def evaluate_window(self, window: List[str]) -> int:
        """Evaluate a 4-piece window"""
        score = 0
        ai_count = window.count('Y')
        human_count = window.count('R')
        empty_count = window.count('')
        
        if ai_count == 4:
            score += 100
        elif ai_count == 3 and empty_count == 1:
            score += 10
        elif ai_count == 2 and empty_count == 2:
            score += 2
        
        if human_count == 3 and empty_count == 1:
            score -= 80  # Block human wins
        elif human_count == 2 and empty_count == 2:
            score -= 2
        
        return score
    
    def is_valid_column_on_board(self, board: List[List[str]], column: int) -> bool:
        """Check if a column is valid for dropping a piece on given board"""
        if column < 0 or column >= self.COLS:
            return False
        return board[0][column] == ''
    
    def get_next_open_row_on_board(self, board: List[List[str]], column: int) -> Optional[int]:
        """Get the next available row in a column on given board"""
        for row in range(self.ROWS - 1, -1, -1):
            if board[row][column] == '':
                return row
        return None
    
    def check_winner(self) -> Optional[str]:
        """Check if there's a winner on the current board"""
        return self.check_winner_on_board(self.board)
    
    def check_winner_on_board(self, board: List[List[str]]) -> Optional[str]:
        """Check if there's a winner on the given board"""
        # Check horizontal
        for row in range(self.ROWS):
            for col in range(self.COLS - 3):
                if (board[row][col] != '' and 
                    board[row][col] == board[row][col + 1] == board[row][col + 2] == board[row][col + 3]):
                    return board[row][col]
        
        # Check vertical
        for col in range(self.COLS):
            for row in range(self.ROWS - 3):
                if (board[row][col] != '' and 
                    board[row][col] == board[row + 1][col] == board[row + 2][col] == board[row + 3][col]):
                    return board[row][col]
        
        # Check positive diagonal
        for row in range(self.ROWS - 3):
            for col in range(self.COLS - 3):
                if (board[row][col] != '' and 
                    board[row][col] == board[row + 1][col + 1] == board[row + 2][col + 2] == board[row + 3][col + 3]):
                    return board[row][col]
        
        # Check negative diagonal
        for row in range(3, self.ROWS):
            for col in range(self.COLS - 3):
                if (board[row][col] != '' and 
                    board[row][col] == board[row - 1][col + 1] == board[row - 2][col + 2] == board[row - 3][col + 3]):
                    return board[row][col]
        
        return None
    
    def is_board_full(self) -> bool:
        """Check if the current board is full"""
        return self.is_board_full_check(self.board)
    
    def is_board_full_check(self, board: List[List[str]]) -> bool:
        """Check if the given board is full"""
        for col in range(self.COLS):
            if board[0][col] == '':
                return False
        return True
    
    def end_game(self, winner: Optional[str]):
        """End the game and show result"""
        self.game_over = True
        self.winner = winner
        
        # Disable all buttons
        for button in self.buttons:
            button.config(state='disabled')
        
        # Show result
        if winner == 'R':
            result_text = "🎉 Congratulations! You won!"
            self.update_status("You won! Excellent Connect 4 strategy!")
        elif winner == 'Y':
            result_text = "🤖 AI wins! Better luck next time!"
            self.update_status("AI won this round. Try again!")
        else:
            result_text = "🤝 It's a draw! Good game!"
            self.update_status("It's a draw! Well played!")
        
        # Update player display to show result
        self.current_player_label.config(
            text=result_text,
            foreground="#0078d4" if winner == 'R' else "#ffa500" if winner == 'Y' else "#666666"
        )
        
        # Notify game manager of game end
        if self.end_game_callback:
            winner_name = "player" if winner == 'R' else "ai" if winner == 'Y' else None
            self.end_game_callback(winner_name)
        else:
            # Show popup with result if no callback
            messagebox.showinfo("Game Over", result_text)
    
    def reset_game(self):
        """Reset the game to initial state"""
        # Reset game state
        self.board = [['' for _ in range(self.COLS)] for _ in range(self.ROWS)]
        self.current_player = 'R'
        self.game_over = False
        self.winner = None
        self.move_count = 0
        self.last_move = None
        
        # Reset UI
        for row in self.board_buttons:
            for button in row:
                button.config(text='', bg='#f0f0f0')
        
        for button in self.buttons:
            button.config(state='normal')
        
        self.update_player_display()
        self.update_status("New game started! Your turn.")
    
    def update_player_display(self):
        """Update the current player display"""
        if self.current_player == 'R':
            self.current_player_label.config(
                text="Your Turn (Red)",
                foreground="#d13438"
            )
        else:
            self.current_player_label.config(
                text="AI Turn (Yellow)",
                foreground="#ffa500"
            )
    
    def update_status(self, message: str):
        """Update status message"""
        if self.status_callback:
            self.status_callback(message)
    
    def back_to_selection(self):
        """Return to game selection"""
        if self.back_callback:
            self.back_callback()
    
    def get_game_state(self) -> Connect4State:
        """Get current game state"""
        return Connect4State(
            board=copy.deepcopy(self.board),
            current_player=self.current_player,
            winner=self.winner,
            game_over=self.game_over,
            move_count=self.move_count,
            last_move=self.last_move
        )